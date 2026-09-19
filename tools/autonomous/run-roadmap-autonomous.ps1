#Requires -Version 5.1
<#
.SYNOPSIS
  Persistent orchestrator: one clean Cursor Agent session per cycle until technical completion.
#>
[CmdletBinding()]
param(
    [int]$MaxCycles = 80,
    [int]$AgentTimeoutMinutes = 120,
    [int]$CiTimeoutMinutes = 30,
    [string]$ExpectedBranch = "feat/official-public-ingest",
    [string]$InitialHead = "1d7a601",
    [int]$PullRequest = 2,
    [switch]$PreflightOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

function Get-RepoRoot {
    $dir = (Resolve-Path (Get-Location)).Path
    if (-not (Test-Path (Join-Path $dir "AGENTS.md")) -or -not (Test-Path (Join-Path $dir ".git"))) {
        throw "Execute na raiz do repositório auditoria-nacional."
    }
    return $dir
}

function Resolve-Bin {
    param([string[]]$Names)
    foreach ($name in $Names) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    $extra = @(
        (Join-Path $env:USERPROFILE ".local\bin\agent.exe"),
        (Join-Path $env:USERPROFILE ".local\bin\agent.cmd"),
        (Join-Path $env:USERPROFILE ".local\bin\agent"),
        (Join-Path $env:LOCALAPPDATA "cursor-agent\agent.cmd"),
        (Join-Path $env:LOCALAPPDATA "cursor-agent\cursor-agent.cmd"),
        "C:\Program Files\GitHub CLI\gh.exe"
    )
    foreach ($path in $extra) {
        if (Test-Path $path) { return $path }
    }
    return $null
}

function Test-DiskHeadroom {
    param(
        [string]$Path,
        [double]$MinFreeRatio = 0.15,
        [double]$MinFreeBytes = 1GB
    )
    $root = [System.IO.Path]::GetPathRoot((Resolve-Path $Path))
    $letter = $root.Substring(0, 1)
    $drive = Get-PSDrive -Name $letter
    $total = [double]$drive.Used + [double]$drive.Free
    $free = [double]$drive.Free
    if ($free -lt $MinFreeBytes) {
        throw ("Espaço livre {0:N1} GB abaixo do mínimo operacional {1:N1} GB." -f ($free / 1GB), ($MinFreeBytes / 1GB))
    }
    if ($total -le 0) { return $false }
    $ratio = $free / $total
    if ($ratio -lt $MinFreeRatio) {
        Write-Log $LogPath ("DISK_LOW free={0:P1} min={1:P0} bytes={2}" -f $ratio, $MinFreeRatio, [int64]$free)
        return $true
    }
    return $false
}

function Get-GitHead {
    return (git rev-parse HEAD).Trim()
}

function Test-Ancestor {
    param([string]$Ancestor, [string]$Head)
    git merge-base --is-ancestor $Ancestor $Head
    return ($LASTEXITCODE -eq 0)
}

function Get-LastProtocolValue {
    param([string]$Text, [string]$Prefix)
    $lines = $Text -split "`r?`n" | Where-Object { $_.Trim() -ne "" }
    for ($i = $lines.Length - 1; $i -ge 0; $i--) {
        if ($lines[$i] -like "$Prefix*") {
            return $lines[$i].Trim()
        }
    }
    return $null
}

function Write-Log {
    param([string]$Path, [string]$Message)
    $line = "{0:o} {1}" -f (Get-Date).ToUniversalTime(), $Message
    Add-Content -Path $Path -Value $line -Encoding UTF8
    Write-Host $line
}

$RepoRoot = Get-RepoRoot
Set-Location $RepoRoot
$env:Path = @(
    (Join-Path $env:USERPROFILE ".local\bin"),
    (Join-Path $env:LOCALAPPDATA "cursor-agent"),
    $env:Path
) -join ";"
$Runtime = Join-Path $RepoRoot ".cursor-autonomous"
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
$LogPath = Join-Path $Runtime "orchestrator.log"
$LockPath = Join-Path $Runtime "orchestrator.lock"
$PidPath = Join-Path $Runtime "orchestrator.pid"
$StopPath = Join-Path $Runtime "STOP"
$CompletePath = Join-Path $Runtime "COMPLETE"
$MaxPath = Join-Path $Runtime "MAX_CYCLES_REACHED"

$AgentCmd = Join-Path $env:LOCALAPPDATA "cursor-agent\agent.cmd"
if (Test-Path $AgentCmd) {
    $Agent = $AgentCmd
}
else {
    $Agent = Resolve-Bin @("agent")
}
$Gh = Resolve-Bin @("gh", "gh.exe")
if (-not $Gh) { $Gh = "C:\Program Files\GitHub CLI\gh.exe" }

function Invoke-Preflight {
    if (-not $Agent -or -not (Test-Path $Agent)) { throw "Cursor CLI 'agent' não encontrado. Instale com irm https://cursor.com/install?win32=true | iex" }
    Write-Host "agent=$Agent"
    if (-not (Test-Path $Gh)) { throw "GitHub CLI gh não encontrado." }
    & $Gh --version | Out-Host
    & $Gh auth status | Out-Host
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if ($branch -ne $ExpectedBranch) {
        throw "Branch atual '$branch' != '$ExpectedBranch'."
    }
    $head = Get-GitHead
    if (-not (Test-Ancestor -Ancestor $InitialHead -Head $head)) {
        throw "HEAD $head não deriva de $InitialHead."
    }
    $porcelain = git status --porcelain
    if ($porcelain) {
        throw "Working tree suja. Commit ou preserve alterações humanas antes de orquestrar.`n$porcelain"
    }
    $script:DiskConstrained = Test-DiskHeadroom -Path $RepoRoot
    Write-Log $LogPath "PREFLIGHT_OK head=$head branch=$branch agent=$Agent disk_constrained=$script:DiskConstrained"
}

function Test-Lock {
    if (Test-Path $LockPath) {
        $old = Get-Content $LockPath -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($old -match "^\d+$") {
            $alive = Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue
            if ($alive) {
                throw "Orquestrador já em execução PID $old."
            }
        }
        Remove-Item $LockPath -Force
    }
    $PID.ToString() | Set-Content $LockPath -Encoding ASCII
    $PID.ToString() | Set-Content $PidPath -Encoding ASCII
}

function Invoke-AgentCycle {
    param(
        [string]$Kind,
        [string]$Prompt,
        [string[]]$ExtraArgs,
        [string]$OutFile
    )
    $dir = [System.IO.Path]::GetDirectoryName($OutFile)
    $stdout = Join-Path $dir "$Kind-stdout.txt"
    $stderr = Join-Path $dir "$Kind-stderr.txt"
    $payloadPath = Join-Path $dir "$Kind-payload.json"
    $runner = Join-Path $dir "$Kind-runner.ps1"
    $argList = @("-p", "--trust", "--workspace", $RepoRoot) + @($ExtraArgs) + @($Prompt)
    $payload = @{
        agent = $Agent
        cwd   = $RepoRoot
        args  = $argList
    } | ConvertTo-Json -Depth 6
    Set-Content -Path $payloadPath -Value $payload -Encoding UTF8
    $runnerText = @'
param([string]$PayloadPath, [string]$StdoutPath, [string]$StderrPath)
$ErrorActionPreference = "Continue"
$payload = Get-Content -LiteralPath $PayloadPath -Raw -Encoding UTF8 | ConvertFrom-Json
Set-Location -LiteralPath $payload.cwd
$argArray = @($payload.args | ForEach-Object { [string]$_ })
$out = & $payload.agent @argArray 2>&1 | Out-String
$code = $LASTEXITCODE
Set-Content -LiteralPath $StdoutPath -Value $out -Encoding UTF8
Set-Content -LiteralPath $StderrPath -Value ("EXIT=" + $code) -Encoding UTF8
exit $code
'@
    Set-Content -Path $runner -Value $runnerText -Encoding UTF8
    Write-Log $LogPath "AGENT_START kind=$Kind"
    $p = Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $runner,
        "-PayloadPath", $payloadPath,
        "-StdoutPath", $stdout,
        "-StderrPath", $stderr
    ) -WorkingDirectory $RepoRoot -PassThru -WindowStyle Hidden
    if (-not $p) { throw "Falha ao iniciar processo agent $Kind." }
    $timeoutMs = [Math]::Max(60000, $AgentTimeoutMinutes * 60000)
    $waited = 0
    $slice = 60000
    $finished = $false
    while ($waited -lt $timeoutMs) {
        if ($p.WaitForExit($slice)) { $finished = $true; break }
        $waited += $slice
        Write-Log $LogPath ("AGENT_WAIT kind={0} pid={1} elapsed_s={2}" -f $Kind, $p.Id, [int]($waited / 1000))
    }
    if (-not $finished) {
        try { Stop-Process -Id $p.Id -Force } catch { }
        throw "Agent $Kind excedeu $AgentTimeoutMinutes min."
    }
    $outText = ""
    $errText = ""
    if (Test-Path $stdout) { $outText = Get-Content $stdout -Raw -Encoding UTF8 }
    if (Test-Path $stderr) { $errText = Get-Content $stderr -Raw -Encoding UTF8 }
    $combined = (($outText + "`n" + $errText).Trim())
    Set-Content -Path $OutFile -Value $combined -Encoding UTF8
    Write-Log $LogPath "AGENT_END kind=$Kind exit=$($p.ExitCode)"
    return @{ ExitCode = $p.ExitCode; Text = $combined }
}

function Wait-PullRequestCi {
    Write-Log $LogPath "CI_WAIT pr=$PullRequest"
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $deadline = (Get-Date).AddMinutes([Math]::Max(5, $CiTimeoutMinutes))
    $ok = $false
    while ((Get-Date) -lt $deadline) {
        & $Gh pr checks $PullRequest | Out-Host
        $code = $LASTEXITCODE
        if ($code -eq 0) {
            $ok = $true
            break
        }
        if ($code -eq 8) {
            Write-Log $LogPath "CI_PENDING"
            Start-Sleep -Seconds 20
            continue
        }
        Write-Log $LogPath "CI_FAIL exit=$code"
        break
    }
    $ErrorActionPreference = $prev
    if ($ok) { Write-Log $LogPath "CI_OK" } elseif (-not $ok -and ((Get-Date) -ge $deadline)) {
        Write-Log $LogPath "CI_TIMEOUT"
    }
    return $ok
}

function Get-QueueFingerprint {
    $queue = Join-Path $RepoRoot "docs/autonomous/ROADMAP-WORK-QUEUE.yaml"
    if (Test-Path $queue) {
        return (Get-FileHash $queue -Algorithm SHA256).Hash
    }
    return "missing"
}

try {
    Invoke-Preflight
    if ($PreflightOnly) {
        Write-Host "PREFLIGHT_ONLY"
        exit 0
    }
    Test-Lock
    Write-Log $LogPath "ORCHESTRATOR_START pid=$PID max=$MaxCycles"

    $noProgress = 0
    $hint = "Selecionar o maior lote seguro PENDING."
    $ciFailed = $false

    for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
        if (Test-Path $StopPath) {
            Write-Log $LogPath "STOP_FILE"
            break
        }
        $script:DiskConstrained = Test-DiskHeadroom -Path $RepoRoot
        if ($script:DiskConstrained) {
            $hint = "$hint DISCO_BAIXO: não iniciar carga oficial volumosa; paginar; checkpoint; limpar caches; manter 15% livre."
        }
        $headBefore = Get-GitHead
        $queueBefore = Get-QueueFingerprint
        $cycleDir = Join-Path $Runtime ("cycle-{0:D3}" -f $cycle)
        New-Item -ItemType Directory -Force -Path $cycleDir | Out-Null
        $builderOut = Join-Path $cycleDir "builder.txt"
        $auditorOut = Join-Path $cycleDir "auditor.txt"

        if ($ciFailed) {
            $hint = "CI da PR #$PullRequest vermelha. Corrigir testes/formato/CI antes de nova funcionalidade."
        }

        $builderPrompt = @"
Leia .cursor/roadmap-controller.md integralmente e execute exatamente um ciclo autônomo de trabalho.
CONTEXTO_ORQUESTRADOR: cycle=$cycle hint=$hint
"@
        $builder = Invoke-AgentCycle -Kind "builder" -Prompt $builderPrompt -ExtraArgs @("--force") -OutFile $builderOut
        $cycleResult = Get-LastProtocolValue -Text $builder.Text -Prefix "CYCLE_RESULT="
        if (-not $cycleResult) { $cycleResult = "CYCLE_RESULT=NO_PROGRESS" }
        Write-Log $LogPath "CYCLE $cycle $cycleResult"

        $headAfter = Get-GitHead
        $queueAfter = Get-QueueFingerprint
        $pushed = $headAfter -ne $headBefore
        $progress = ($pushed -or $queueAfter -ne $queueBefore -or $cycleResult -eq "CYCLE_RESULT=PROGRESSED" -or $cycleResult -eq "CYCLE_RESULT=COMPLETE_CANDIDATE")

        if ($pushed) {
            $ciFailed = -not (Wait-PullRequestCi)
            if ($ciFailed) {
                $hint = "Corrigir CI vermelha da PR #$PullRequest."
                $noProgress = 0
                continue
            }
        }

        if ($cycleResult -eq "CYCLE_RESULT=COMPLETE_CANDIDATE" -or ($progress -and $cycleResult -ne "CYCLE_RESULT=NO_PROGRESS")) {
            $noProgress = 0
            $hint = "Continuar o próximo lote PENDING da fila."
        }
        else {
            $noProgress++
            if ($noProgress -eq 1) {
                $hint = "NO_PROGRESS. Diagnosticar bloqueio, reduzir a fatia e tentar alternativa segura."
            }
            elseif ($noProgress -eq 2) {
                $hint = "Segundo NO_PROGRESS. Diagnosticar causa, registrar evidência e escolher item independente."
            }
            else {
                $hint = "Terceiro NO_PROGRESS no recorte. Concluir estrutura técnica possível, classificar corretamente e mudar de item."
            }
            Write-Log $LogPath "NO_PROGRESS_STREAK=$noProgress"
        }

        $auditorPrompt = @"
Leia .cursor/roadmap-auditor.md integralmente e execute exatamente uma auditoria somente leitura.
Sessão auditora independente do ciclo $cycle.
"@
        $auditor = Invoke-AgentCycle -Kind "auditor" -Prompt $auditorPrompt -ExtraArgs @("--mode=ask") -OutFile $auditorOut
        $verdict = Get-LastProtocolValue -Text $auditor.Text -Prefix "VERDICT="
        $next = Get-LastProtocolValue -Text $auditor.Text -Prefix "NEXT_OBJECTIVE="
        Write-Log $LogPath "AUDITOR $verdict $next"

        if ($verdict -eq "VERDICT=CONTINUE" -and $next) {
            $hint = "NEXT_OBJECTIVE=$next"
        }

        $candidate = ($cycleResult -eq "CYCLE_RESULT=COMPLETE_CANDIDATE") -and ($verdict -eq "VERDICT=COMPLETE")
        if ($candidate) {
            Write-Log $LogPath "COMPLETE_CANDIDATE_CHECKS"
            $verify = Join-Path $RepoRoot "tools/autonomous/verify-roadmap.ps1"
            $prev = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            powershell -NoProfile -ExecutionPolicy Bypass -File $verify
            $verifyOk = ($LASTEXITCODE -eq 0)
            $ErrorActionPreference = $prev
            $ciOk = Wait-PullRequestCi
            $clean = -not (git status --porcelain)
            $auditor2Out = Join-Path $cycleDir "auditor-2.txt"
            $auditor2 = Invoke-AgentCycle -Kind "auditor2" -Prompt $auditorPrompt -ExtraArgs @("--mode=ask") -OutFile $auditor2Out
            $verdict2 = Get-LastProtocolValue -Text $auditor2.Text -Prefix "VERDICT="
            Write-Log $LogPath "COMPLETE_GATES verify=$verifyOk ci=$ciOk clean=$clean auditor2=$verdict2"
            if ($verifyOk -and $ciOk -and $clean -and $verdict2 -eq "VERDICT=COMPLETE") {
                Set-Content $CompletePath -Value ("head={0}`ncompleted_at={1:o}" -f (Get-GitHead), (Get-Date).ToUniversalTime()) -Encoding UTF8
                Write-Log $LogPath "ORCHESTRATOR_COMPLETE"
                exit 0
            }
            $hint = "Candidato a completo rejeitado. Corrigir gates e continuar."
        }
    }

    Set-Content $MaxPath -Value ("head={0}`ncycles={1}" -f (Get-GitHead), $MaxCycles) -Encoding UTF8
    Write-Log $LogPath "MAX_CYCLES_REACHED"
    exit 2
}
catch {
    Write-Log $LogPath ("ORCHESTRATOR_ERROR " + $_.Exception.Message)
    throw
}
finally {
    if (Test-Path $LockPath) {
        $lockPid = Get-Content $LockPath -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($lockPid -eq "$PID") { Remove-Item $LockPath -Force -ErrorAction SilentlyContinue }
    }
}
