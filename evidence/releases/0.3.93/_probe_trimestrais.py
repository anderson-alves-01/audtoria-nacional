"""Probe BCB OLINDA ExpectativasMercadoTrimestrais indicators (PUBLIC_OPEN)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from urllib.parse import quote

BASE = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoTrimestrais"
)
INDICATORS = [
    "IPCA",
    "IPCA Livres",
    "IPCA Serviços",
    "IPCA Administrados",
    "IPCA Alimentação no domicílio",
    "IPCA Bens industrializados",
    "Selic",
    "Câmbio",
    "PIB Total",
    "PIB Serviços",
    "PIB Agropecuária",
    "PIB Indústria",
    "IGP-M",
    "IGP-DI",
    "INPC",
    "IPA-M",
    "IPA-DI",
    "IPCA-15",
    "IPC-Fipe",
    "Produção industrial",
]


def build_url(indicator: str, base_calculo: int, top: int = 8) -> str:
    encoded = quote(indicator, safe="")
    return (
        f"{BASE}?$top={top}&$format=json&"
        f"$filter=Indicador%20eq%20%27{encoded}%27%20and%20baseCalculo%20eq%20{base_calculo}&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    )


def main() -> None:
    out = Path("evidence/releases/0.3.93")
    out.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    for ind in INDICATORS:
        for bc in (1, 0):
            url = build_url(ind, bc)
            try:
                with urllib.request.urlopen(url, timeout=45) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                values = payload.get("value") or []
                first = values[0] if values else None
                row = {
                    "indicator": ind,
                    "baseCalculo": bc,
                    "count": len(values),
                    "firstData": first.get("Data") if first else None,
                    "firstMediana": first.get("Mediana") if first else None,
                    "firstRef": first.get("DataReferencia") if first else None,
                    "url": url,
                }
                summary.append(row)
                print(
                    f"{ind} bc={bc} count={len(values)} "
                    f"data={row['firstData']} med={row['firstMediana']} "
                    f"ref={row['firstRef']}"
                )
                if values:
                    safe = "".join(
                        c if c.isalnum() or c in "-_" else "-" for c in ind
                    ).strip("-").lower()
                    path = out / (
                        f"bcb-olinda-expectativas-{safe}-trimestrais-bc{bc}-top8-probe.json"
                    )
                    path.write_text(
                        json.dumps(payload, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
            except Exception as exc:  # noqa: BLE001 — probe script
                print(f"{ind} bc={bc} FAIL {exc}")
                summary.append(
                    {
                        "indicator": ind,
                        "baseCalculo": bc,
                        "count": -1,
                        "error": str(exc),
                        "url": url,
                    }
                )
    (out / "probe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("DONE", len(summary))


if __name__ == "__main__":
    main()
