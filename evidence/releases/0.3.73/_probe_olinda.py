"""One-shot probe for BCB OLINDA Resultado nominal."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "official-snapshots"
EVIDENCE = Path(__file__).resolve().parent

BASE = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoAnuais"
)


def build_url(*, indicator: str, base_calculo: int) -> str:
    enc_ind = quote(indicator, safe="")
    return (
        f"{BASE}?$top=8&$format=json&"
        f"$filter=Indicador%20eq%20%27{enc_ind}%27%20and%20baseCalculo%20eq%20{base_calculo}&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    )


def fetch(name: str, url: str) -> dict:
    print(name, url)
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.73"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = resp.read()
    probe = EVIDENCE / f"bcb-olinda-expectativas-{name}-anuais-top8-probe.json"
    fixture = FIXTURES / f"bcb-olinda-expectativas-{name}-anuais-top8.json"
    probe.write_bytes(body)
    fixture.write_bytes(body)
    data = json.loads(body)
    rows = data.get("value") or []
    print(name, "rows", len(rows), "first", rows[0] if rows else None)
    return data


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    fetch("resultado-nominal", build_url(indicator="Resultado nominal", base_calculo=1))


if __name__ == "__main__":
    main()
