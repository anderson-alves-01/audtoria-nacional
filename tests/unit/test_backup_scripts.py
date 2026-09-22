import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def test_backup_script_dry_run_prints_plan_without_writing(tmp_path: Path) -> None:
    output = tmp_path / "sirta.dump"
    if sys.platform.startswith("win"):
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPTS / "postgres-backup.ps1"),
            "-DryRun",
            "-Output",
            str(output),
        ]
    else:
        cmd = [
            "bash",
            str(SCRIPTS / "postgres-backup.sh"),
            "--dry-run",
            "--output",
            str(output),
        ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr or completed.stdout
    combined = (completed.stdout or "") + (completed.stderr or "")
    assert "pg_dump" in combined
    assert "DRY-RUN" in combined
    assert not output.exists()


def test_restore_script_dry_run_reports_checksum(tmp_path: Path) -> None:
    dump = tmp_path / "fixture.dump"
    payload = b"SIRTA-LOCAL-DUMP-FIXTURE"
    dump.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest().upper()
    if sys.platform.startswith("win"):
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPTS / "postgres-restore.ps1"),
            "-DryRun",
            "-InputFile",
            str(dump),
        ]
    else:
        cmd = [
            "bash",
            str(SCRIPTS / "postgres-restore.sh"),
            "--dry-run",
            "--input",
            str(dump),
        ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr or completed.stdout
    combined = (completed.stdout or "") + (completed.stderr or "")
    assert "pg_restore" in combined
    assert "DRY-RUN" in combined
    # Scripts may print lower (sha256sum) or upper (Get-FileHash).
    assert expected.upper() in combined.upper()
    assert "sha256=" in combined.lower()


def test_tool_call_audit_prefix() -> None:
    from unittest.mock import MagicMock
    from uuid import uuid4

    from sirta_api.application.dlp import record_tool_call_audit
    from sirta_api.domain.authorization import AccessContext
    from sirta_api.domain.identities import Role

    session = MagicMock()
    context = AccessContext(
        user_id=uuid4(),
        tenant_id=uuid4(),
        territory_id=uuid4(),
        purpose_id=uuid4(),
        role=Role.ANALYST,
        purpose_expires_at=None,
        username="analyst",
    )
    record_tool_call_audit(
        session,
        context=context,
        tool_name="official_ingest",
        route="/v1/data-sources/IBGE-SIDRA/ingest",
        outcome="allowed",
    )
    assert session.add.called
    event = session.add.call_args.args[0]
    assert event.action == "tool.official_ingest"
    assert event.resource_type == "tool_call"
