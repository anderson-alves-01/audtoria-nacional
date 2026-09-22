"""One-shot probe for BCB OLINDA Taxa de desocupacao."""
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
ODATA = chr(36)


def build_url(*, indicator: str, base_calculo: int) -> str:
    enc_ind = quote(indicator, safe="")
    return (
        f"{BASE}?{ODATA}top=8&{ODATA}format=json&"
        f"{ODATA}filter=Indicador%20eq%20%27{enc_ind}%27%20and%20baseCalculo%20eq%20{base_calculo}&"
        f"{ODATA}orderby=Data%20desc,DataReferencia%20asc&"
        f"{ODATA}select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    )


def fetch(name: str, url: str) -> dict:
    print(name, url)
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.75"})
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
    indicator = "Taxa de desocupa" + "\u00e7\u00e3o"
    fetch(
        "taxa-desocupacao",
        build_url(indicator=indicator, base_calculo=1),
    )


if __name__ == "__main__":
    main()
