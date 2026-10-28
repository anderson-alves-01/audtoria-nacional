# ruff: noqa: E501
"""Reexecuta a verificação do SPED e grava a evidência da homologação do Simulador.

Somente leitura sobre os originais. Roda os três scripts já existentes (verificação de hash,
reconciliação e auditoria das omissões), confere invariantes e escreve
`evidence/ops/sped-homologacao-reconciliacao-20261028.md`. Não carrega nada no banco, não altera
os originais e não corrige quantidade alguma.

Uso:
    python tools/ops/sped-homologacao-evidence.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.domain.sped_operations import (  # noqa: E402
    CLASS_CONFIRMED,
    CLASS_PENDING,
    DIRECTION_RECEIVED,
    DIRECTION_SENT,
    TRANSFER_RECEIVED_CFOPS,
    TRANSFER_SENT_CFOPS,
    assert_single_direction,
    classify_cfop_sirta,
)

EVIDENCE = ROOT / "evidence" / "ops" / "sped-homologacao-reconciliacao-20261028.md"
RECONCILE = ROOT / "evidence" / "ops" / "sped-reconciliacao-20261028.md"
AUDIT = ROOT / "evidence" / "ops" / "sped-auditoria-omissoes-20261028.md"
ORIGINALS = "docs/data/originais"
SCRIPTS = (
    "tools/ops/sped-source-verify.py",
    "tools/ops/sped-source-reconcile.py",
    "tools/ops/sped-omission-audit.py",
)


@dataclass
class Check:
    id: str
    description: str
    expected: str
    observed: str

    @property
    def passed(self) -> bool:
        return self.expected == self.observed


def _int(text: str) -> int:
    return int(text.replace(".", "").replace(",", ""))


def _run(script: str) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def _find(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else "AUSENTE"


def main() -> int:
    outputs: dict[str, tuple[int, str]] = {script: _run(script) for script in SCRIPTS}
    reconcile = RECONCILE.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    checks: list[Check] = []

    verify_code, verify_out = outputs[SCRIPTS[0]]
    checks.append(
        Check(
            "SP-01",
            "Hash SHA-256 e tamanho dos 2 originais e da planilha consolidada conferem",
            "0 e 3 OK",
            f"{verify_code} e {verify_out.count('OK ')} OK",
        )
    )
    changed = subprocess.run(
        ["git", "status", "--porcelain", "--", ORIGINALS],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    checks.append(
        Check(
            "SP-02",
            "Os originais em docs/data/originais não foram alterados",
            "limpo",
            changed or "limpo",
        )
    )
    cells = _find(r"consolidada: (\d+)\.", reconcile)
    equal = _find(r"original \(coluna Quantidade NF-e\): (\d+),", reconcile)
    checks.append(Check("SP-03", "46.825 células reproduzidas (planilha)", "46825", cells))
    checks.append(Check("SP-04", "46.825 células iguais ao original", "46825", equal))
    checks.append(
        Check(
            "SP-05",
            "Células diferentes ou sem correspondência no original",
            "0 e 0",
            f"{_find(r'Diferentes: (\d+)\.', reconcile)} e "
            f"{_find(r'correspondência no original: (\d+)', reconcile)}",
        )
    )
    absent = _find(r"ausentes da planilha: (\d+),", reconcile)
    legit = _find(r"dos quais (\d+) por regra", reconcile)
    undue = _find(r"; (\d+) sem regra que explique", reconcile)
    checks.append(
        Check("SP-06", "Ausentes = legítimas + indevidas", absent, str(int(legit) + int(undue)))
    )
    checks.append(Check("SP-07", "Omissões sem regra publicada", "1041", undue))
    checks.append(Check("SP-08", "Células ausentes no total", "22343", absent))

    received_cells = _int(_find(r"\| TRANSFERENCIA_RECEBIDA \| (\d[\d.]*) \|", audit))
    pending_cells = _int(_find(r"\| PENDENTE_CLASSIFICACAO \| (\d[\d.]*) \|", audit))
    received_nfe = _int(_find(r"\| TRANSFERENCIA_RECEBIDA \| \d[\d.]* \| (\d[\d.]*) \|", audit))
    pending_nfe = _int(_find(r"\| PENDENTE_CLASSIFICACAO \| \d[\d.]* \| (\d[\d.]*) \|", audit))
    checks.append(
        Check(
            "SP-09",
            "1.041 omissões = recebidas confirmadas + pendentes (células)",
            "1041",
            str(received_cells + pending_cells),
        )
    )
    checks.append(
        Check(
            "SP-10",
            "268.317.945 NF-e = recebidas confirmadas + pendentes",
            "268317945",
            str(received_nfe + pending_nfe),
        )
    )
    checks.append(
        Check(
            "SP-11",
            "Recebidas confirmadas (células e NF-e)",
            "844 e 132237096",
            f"{received_cells} e {received_nfe}",
        )
    )
    checks.append(
        Check(
            "SP-12",
            "Pendentes de classificação (células e NF-e)",
            "197 e 136080849",
            f"{pending_cells} e {pending_nfe}",
        )
    )

    # Classificação dos CFOPs de transferência, pela tabela oficial.
    received_ok = all(
        (c := classify_cfop_sirta(code)).direction == DIRECTION_RECEIVED
        and c.status == CLASS_CONFIRMED
        for code in TRANSFER_RECEIVED_CFOPS
    )
    sent_ok = all(
        (c := classify_cfop_sirta(code)).direction == DIRECTION_SENT and c.status == CLASS_CONFIRMED
        for code in TRANSFER_SENT_CFOPS
    )
    checks.append(
        Check(
            "SP-13",
            "CFOPs de transferência confirmados (recebidos e remetidos) têm direção própria",
            f"True, True, {len(TRANSFER_RECEIVED_CFOPS)}, {len(TRANSFER_SENT_CFOPS)}",
            f"{received_ok}, {sent_ok}, {len(TRANSFER_RECEIVED_CFOPS)}, {len(TRANSFER_SENT_CFOPS)}",
        )
    )
    pending_codes = ("1159", "2159", "1190", "2170", "1155", "1156", "1157", "1158", "5154", "5157")
    still_pending = [c for c in pending_codes if classify_cfop_sirta(c).status == CLASS_PENDING]
    checks.append(
        Check(
            "SP-14",
            "CFOPs sem classificação comprovada continuam pendentes",
            ",".join(pending_codes),
            ",".join(still_pending),
        )
    )
    try:
        assert_single_direction([DIRECTION_RECEIVED, DIRECTION_SENT])
        mixed = "aceitou a mistura"
    except ValueError:
        mixed = "recusou a mistura"
    checks.append(
        Check("SP-15", "Somar recebidas e remetidas é recusado", "recusou a mistura", mixed)
    )
    checks.append(
        Check(
            "SP-16",
            "Nenhum script saiu com erro",
            "0, 0, 0",
            ", ".join(str(outputs[script][0]) for script in SCRIPTS),
        )
    )

    lines = [
        "# Evidência SPED da homologação do Simulador (28/10/2026)",
        "",
        f"Gerado em {datetime.now(UTC):%Y-%m-%d %H:%M} UTC por `tools/ops/sped-homologacao-evidence.py`. "
        "Somente leitura sobre os originais. Nenhuma quantidade foi alterada e nada foi carregado no banco.",
        "",
        "## Comandos executados",
        "",
        *[f"- `python {script}` (código de saída {outputs[script][0]})" for script in SCRIPTS],
        "",
        "## Saída da verificação de hash",
        "",
        "```",
        verify_out,
        "```",
        "",
        "## Verificações",
        "",
        "| ID | Verificação | Esperado | Observado | Resultado |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {c.id} | {c.description} | {c.expected} | {c.observed} | {'APROVADO' if c.passed else 'REPROVADO'} |"
            for c in checks
        ],
        "",
        f"Resultado: {sum(c.passed for c in checks)} de {len(checks)} verificações aprovadas.",
        "",
        "## Origem dos números",
        "",
        "- Reconciliação (46.825 células, 22.343 ausentes): `evidence/ops/sped-reconciliacao-20261028.md`.",
        "- Auditoria das 1.041 omissões e reclassificação por CFOP: `evidence/ops/sped-auditoria-omissoes-20261028.md` e `evidence/ops/sped-omissoes-1041-20261028.csv`.",
        "- Tabela oficial de CFOP (Sefaz-PE, `cfop.htm`, lida em 2026-10-28): só os CFOPs listados ali como transferência são confirmados.",
        "",
        "Limites: a definição de `Quantidade NF-e` não existe nas fontes e a planilha não traz as entradas por transferência. "
        "Por isso nenhum indicador do SPED é promovido a CONFERIDO.",
        "",
    ]
    EVIDENCE.write_text("\n".join(lines), encoding="utf-8")
    failed = [c for c in checks if not c.passed]
    for check in failed:
        print(f"REPROVADO {check.id}: esperado {check.expected}, observado {check.observed}")
    print(f"{len(checks) - len(failed)} de {len(checks)} verificações aprovadas")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
