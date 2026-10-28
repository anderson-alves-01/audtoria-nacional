"""Verify that the preserved SPED source files still match the recorded checksums.

Read only and offline. It compares the sha256 and size of the two official .ods files in
docs/data/originais/ with the manifest that tools/ops/sped-source-fetch.py wrote
(evidence/ops/sped-originais-20261028.txt), and the consolidated workbook with the checksum
recorded when it was validated and ingested (evidence/ops/prod-sped-ingest-20261027.txt).
It never rewrites a file and never downloads anything.

Usage: python tools/ops/sped-source-verify.py
Exit code: 0 when every present file matches, 1 on any mismatch or missing official original.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "evidence" / "ops" / "sped-originais-20261028.txt"
ORIGINAIS = ROOT / "docs" / "data" / "originais"
WORKBOOK = ROOT / "docs" / "data" / "Consolidado_Operacoes_UF_2021_2025_SPED.xlsx"
# Recorded in evidence/ops/prod-sped-ingest-20261027.txt and current-state.yaml.
WORKBOOK_SHA256 = "1091967dd768b72152cc4c4a9b01b8637eebe45827c268f658ad462044e02cf3"


def read_manifest(path: Path) -> list[tuple[str, int, str]]:
    """Return (relative file, bytes, sha256) for every entry in the fetch manifest."""
    entries: list[tuple[str, int, str]] = []
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("file="):
            current = stripped.removeprefix("file=")
        elif current and (match := re.match(r"bytes=(\d+) sha256=([0-9a-f]{64})$", stripped)):
            entries.append((current, int(match.group(1)), match.group(2)))
            current = None
    return entries


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(entries: list[tuple[str, int, str]], root: Path) -> list[str]:
    """Return one problem string per mismatch. An empty list means everything matches."""
    problems: list[str] = []
    if not entries:
        problems.append("manifesto sem entradas")
    for relative, size, expected in entries:
        path = root / relative
        if not path.is_file():
            problems.append(f"AUSENTE {relative}")
            continue
        if path.stat().st_size != size:
            problems.append(f"TAMANHO {relative}: {path.stat().st_size} != {size}")
            continue
        actual = sha256_of(path)
        if actual != expected:
            problems.append(f"SHA256 {relative}: {actual} != {expected}")
    return problems


def main() -> int:
    if not MANIFEST.is_file():
        print(f"manifesto ausente: {MANIFEST}")
        return 1
    entries = read_manifest(MANIFEST)
    problems = verify(entries, ROOT)
    for relative, _size, sha in entries:
        status = "OK" if not any(relative in problem for problem in problems) else "FALHA"
        print(f"{status} {relative} sha256={sha}")
    if WORKBOOK.is_file():
        actual = sha256_of(WORKBOOK)
        ok = actual == WORKBOOK_SHA256
        print(f"{'OK' if ok else 'FALHA'} {WORKBOOK.relative_to(ROOT).as_posix()} sha256={actual}")
        if not ok:
            problems.append(f"SHA256 planilha consolidada: {actual} != {WORKBOOK_SHA256}")
    else:
        print("AVISO planilha consolidada ausente (arquivo fora do git); nada a comparar")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
