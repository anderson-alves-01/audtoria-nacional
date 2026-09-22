"""Probe BCB OLINDA for IPCA-15."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.parse import quote

INDICATOR = "IPCA-15"
ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "official-snapshots"
    / "bcb-olinda-expectativas-ipca-15-anuais-top8.json"
)
PROBE = Path(__file__).with_name("bcb-olinda-expectativas-ipca-15-anuais-top8-probe.json")


def main() -> None:
    encoded = quote(INDICATOR, safe="")
    filter_clause = f"Indicador%20eq%20%27{encoded}%27%20and%20baseCalculo%20eq%200"
    url = (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        "ExpectativasMercadoAnuais?$top=8&$format=json&"
        f"$filter={filter_clause}&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    )
    print("URL:", url)
    with urllib.request.urlopen(url, timeout=60) as resp:
        raw = resp.read()
    data = json.loads(raw.decode("utf-8"))
    assert len(data["value"]) == 8, data
    assert data["value"][0]["Indicador"] == INDICATOR
    assert data["value"][0]["baseCalculo"] == 0
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    FIXTURE.write_text(compact, encoding="utf-8")
    PROBE.write_text(compact, encoding="utf-8")
    print("first:", data["value"][0])
    print("Mediana:", data["value"][0]["Mediana"])
    print("written:", FIXTURE)
    print("written:", PROBE)


if __name__ == "__main__":
    main()
