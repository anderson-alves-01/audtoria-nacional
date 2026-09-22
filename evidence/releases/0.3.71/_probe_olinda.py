"""One-shot probe for BCB OLINDA Dívida + Balança Saldo fixtures."""
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


def build_url(*, indicator: str, base_calculo: int, detalhe: str | None = None) -> str:
    enc_ind = quote(indicator, safe="")
    filters = [f"Indicador%20eq%20%27{enc_ind}%27", f"baseCalculo%20eq%20{base_calculo}"]
    select = "Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    if detalhe:
        enc_det = quote(detalhe, safe="")
        filters.insert(1, f"IndicadorDetalhe%20eq%20%27{enc_det}%27")
        select = "Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    joined = "%20and%20".join(filters)
    return (
        f"{BASE}?$top=8&$format=json&$filter={joined}&"
        f"$orderby=Data%20desc,DataReferencia%20asc&$select={select}"
    )


def fetch(name: str, url: str) -> dict:
    print(name, url)
    with urllib.request.urlopen(url, timeout=60) as resp:
        body = resp.read()
    probe = EVIDENCE / f"bcb-olinda-expectativas-{name}-anuais-top8-probe.json"
    fixture = FIXTURES / f"bcb-olinda-expectativas-{name}-anuais-top8.json"
    probe.write_bytes(body)
    fixture.write_bytes(body)
    data = json.loads(body)
    print(name, "rows", len(data["value"]), "first", data["value"][0])
    return data


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    fetch(
        "divida-liquida",
        build_url(indicator="Dívida líquida do setor público", base_calculo=0),
    )
    fetch(
        "balanca-saldo",
        build_url(indicator="Balança comercial", base_calculo=1, detalhe="Saldo"),
    )


if __name__ == "__main__":
    main()
