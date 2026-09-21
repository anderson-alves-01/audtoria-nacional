"""One-shot probe for BCB OLINDA IPCA Livres / IPCA Servicos."""
from __future__ import annotations

import json
import urllib.error
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


def build_url(*, indicator: str, base_calculo: int, detalhe: str | None = None) -> str:
    enc_ind = quote(indicator, safe="")
    if detalhe:
        enc_det = quote(detalhe, safe="")
        filt = (
            f"Indicador%20eq%20%27{enc_ind}%27%20and%20"
            f"IndicadorDetalhe%20eq%20%27{enc_det}%27%20and%20"
            f"baseCalculo%20eq%20{base_calculo}"
        )
        select = "Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    else:
        filt = f"Indicador%20eq%20%27{enc_ind}%27%20and%20baseCalculo%20eq%20{base_calculo}"
        select = "Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    return (
        f"{BASE}?{ODATA}top=8&{ODATA}format=json&"
        f"{ODATA}filter={filt}&"
        f"{ODATA}orderby=Data%20desc,DataReferencia%20asc&"
        f"{ODATA}select={select}"
    )


def fetch(name: str, url: str, *, write_fixture: bool = False) -> list[dict]:
    print(name, url)
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.78"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        print(name, "HTTP", exc.code, exc.read()[:200])
        return []
    probe = EVIDENCE / f"bcb-olinda-expectativas-{name}-anuais-top8-probe.json"
    probe.write_bytes(body)
    data = json.loads(body)
    rows = data.get("value") or []
    print(name, "rows", len(rows), "first", rows[0] if rows else None)
    if write_fixture and rows:
        fixture = FIXTURES / f"bcb-olinda-expectativas-{name}-anuais-top8.json"
        fixture.write_bytes(body)
        print("wrote fixture", fixture)
    return rows


def discover_ipca_variants() -> None:
    """Pull recent IPCA rows with IndicadorDetalhe to see published variants."""
    url = (
        f"{BASE}?{ODATA}top=50&{ODATA}format=json&"
        f"{ODATA}filter=Indicador%20eq%20%27IPCA%27&"
        f"{ODATA}orderby=Data%20desc&"
        f"{ODATA}select=Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,baseCalculo"
    )
    print("=== discover", url)
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.78"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
    rows = data.get("value") or []
    pairs: set[tuple[str, str, int]] = set()
    for row in rows:
        pairs.add(
            (
                str(row.get("Indicador") or ""),
                str(row.get("IndicadorDetalhe") or ""),
                int(row.get("baseCalculo") or 0),
            )
        )
    print("distinct IPCA (Indicador, Detalhe, base):")
    for item in sorted(pairs):
        print(" ", item)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    discover_ipca_variants()

    candidates: list[tuple[str, str, int, str | None]] = [
        ("ipca-livres", "IPCA Livres", 1, None),
        ("ipca-servicos", "IPCA Serviços", 1, None),
        ("ipca-administrados", "IPCA Administrados", 1, None),
        ("ipca-det-livres", "IPCA", 1, "Livres"),
        ("ipca-det-servicos", "IPCA", 1, "Serviços"),
        ("ipca-det-administrados", "IPCA", 1, "Administrados"),
    ]
    for name, indicator, base, detalhe in candidates:
        fetch(name, build_url(indicator=indicator, base_calculo=base, detalhe=detalhe))


if __name__ == "__main__":
    main()
