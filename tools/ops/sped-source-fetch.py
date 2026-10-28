"""Fetch the two official SPED NF-e statistics files used to check the consolidated workbook.

Read only. Only the two URLs in ALLOWED are ever requested. Dry run by default; pass
--execute to download. Each file is written under docs/data/originais/ and its sha256, size,
URL and date are recorded in evidence/ops/sped-originais-<date>.txt. No credentials, no other
pages, no data is sent anywhere. The downloaded files stay out of git (see .gitignore).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

BASE = "https://www.gov.br/sped/pt-br/centrais-de-conteudo/estatisticas-sped/nf-e"
ALLOWED = {
    "historico_cfop_uf": (
        f"{BASE}/historico-de-quantidades-de-emitentesnf-e-por-cfop-por-uf/nfe-cfop-uf/@@download/file",
        "Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods",
        "Histórico de quantidades de emitentes/NF-e por CFOP por UF (2016 a 2025)",
    ),
    "cfop_mes_2025": (
        f"{BASE}/2025/quantidade-nfe-cfopmes/estat_nfe_cfop_2025_v1_formatada.ods/@@download/file",
        "Estat_NFe_CFOP_2025_v1_formatada.ods",
        "Planilha de Valores Totais e Quantidade de NF-e por CFOP/Mês (2025)",
    ),
}
MAX_BYTES = 20_000_000
ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "docs" / "data" / "originais"


def fetch(url: str) -> bytes:
    if not any(url == allowed[0] for allowed in ALLOWED.values()):
        raise SystemExit(f"URL fora da lista permitida: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "sirta-source-check/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 (fixed https URL)
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise SystemExit("Arquivo maior que o limite de 20 MB; abortado.")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="baixa de fato (padrão: dry-run)")
    args = parser.parse_args()
    now = datetime.now(UTC)
    lines = [f"started={now.isoformat()}", f"mode={'EXECUTE' if args.execute else 'DRY_RUN'}"]
    for key, (url, filename, label) in ALLOWED.items():
        lines.append(f"{key}: {label}")
        lines.append(f"  url={url}")
        if not args.execute:
            continue
        body = fetch(url)
        TARGET.mkdir(parents=True, exist_ok=True)
        (TARGET / filename).write_bytes(body)
        lines.append(f"  file=docs/data/originais/{filename}")
        lines.append(f"  bytes={len(body)} sha256={hashlib.sha256(body).hexdigest()}")
    lines.append("access=GET público somente leitura, sem credenciais, só as duas URLs acima")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.execute:
        out = ROOT / "evidence" / "ops" / f"sped-originais-{now:%Y%m%d}.txt"
        out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
