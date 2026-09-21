"""One-shot probe for BCB OLINDA Resultado primario + Conta corrente."""
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
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.72"})
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


def try_fetch(name: str, indicator: str, base_calculo: int, detalhe: str | None = None) -> bool:
    try:
        data = fetch(
            name,
            build_url(indicator=indicator, base_calculo=base_calculo, detalhe=detalhe),
        )
        return bool(data.get("value"))
    except Exception as exc:  # noqa: BLE001
        print("FAIL", name, type(exc).__name__, exc)
        return False


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    candidates = [
        ("resultado-primario", "Resultado primário", 1, None),
        ("resultado-primario-b0", "Resultado primário", 0, None),
        ("conta-corrente", "Conta corrente", 1, None),
        ("conta-corrente-b0", "Conta corrente", 0, None),
        ("resultado-nominal", "Resultado nominal", 1, None),
        ("resultado-nominal-b0", "Resultado nominal", 0, None),
    ]
    ok = []
    for name, indicator, base, detalhe in candidates:
        if try_fetch(name, indicator, base, detalhe):
            ok.append((name, indicator, base, detalhe))
    print("OK", ok)


if __name__ == "__main__":
    main()
