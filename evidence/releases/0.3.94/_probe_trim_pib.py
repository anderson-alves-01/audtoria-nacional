"""Probe and copy BCB OLINDA Trimestrais PIB setoriais fixtures (PUBLIC_OPEN)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.parse import quote

BASE = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoTrimestrais"
)
INDICATORS = {
    "PIB Serviços": "pib-servicos",
    "PIB Agropecuária": "pib-agropecuaria",
    "PIB Indústria": "pib-industria",
}


def build_url(indicator: str, base_calculo: int = 1, top: int = 8) -> str:
    encoded = quote(indicator, safe="")
    # Percent-encode $ so PowerShell never expands OData params.
    return (
        f"{BASE}?%24top={top}&%24format=json&"
        f"%24filter=Indicador%20eq%20%27{encoded}%27%20and%20baseCalculo%20eq%20{base_calculo}&"
        "%24orderby=Data%20desc,DataReferencia%20asc&"
        "%24select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    )


def main() -> None:
    fix = Path("tests/fixtures/official-snapshots")
    evid = Path("evidence/releases/0.3.94")
    evid.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    for ind, slug in INDICATORS.items():
        url = build_url(ind)
        with urllib.request.urlopen(url, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        values = payload.get("value") or []
        first = values[0] if values else None
        inds = {row.get("Indicador") for row in values}
        if len(values) != 8 or inds != {ind}:
            raise SystemExit(f"unexpected payload for {ind}: n={len(values)} inds={inds}")
        fixture = fix / f"bcb-olinda-expectativas-{slug}-trimestrais-top8.json"
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        fixture.write_text(text, encoding="utf-8")
        probe = evid / f"bcb-olinda-expectativas-{slug}-trimestrais-bc1-top8-probe.json"
        probe.write_text(text, encoding="utf-8")
        row = {
            "indicator": ind,
            "baseCalculo": 1,
            "count": len(values),
            "firstData": first.get("Data") if first else None,
            "firstMediana": first.get("Mediana") if first else None,
            "firstRef": first.get("DataReferencia") if first else None,
            "fixture": str(fixture).replace("\\", "/"),
            "url": url,
        }
        summary.append(row)
        print(
            f"{ind} count={len(values)} data={row['firstData']} "
            f"med={row['firstMediana']} ref={row['firstRef']}"
        )
    (evid / "probe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("DONE", len(summary))


if __name__ == "__main__":
    main()
