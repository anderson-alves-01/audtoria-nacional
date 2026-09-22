"""Diagnose OLINDA connectivity and list distinct annual indicators."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.88"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:  # noqa: BLE001
        return -1, repr(exc)


def main() -> None:
    urls = {
        "ipca_top2": BASE
        + "ExpectativasMercadoAnuais?"
        + urllib.parse.urlencode(
            {
                "$top": "2",
                "$format": "json",
                "$filter": "Indicador eq 'IPCA' and baseCalculo eq 1",
                "$orderby": "Data desc,DataReferencia asc",
                "$select": "Indicador,Data,DataReferencia,Mediana,Media,baseCalculo",
            }
        ),
        "metadata": "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/$metadata",
        "root": "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/",
        # paginate without filter to collect Indicador values
        "sample_unfiltered": BASE
        + "ExpectativasMercadoAnuais?"
        + urllib.parse.urlencode(
            {
                "$top": "100",
                "$format": "json",
                "$select": "Indicador,IndicadorDetalhe,baseCalculo",
                "$orderby": "Indicador",
            }
        ),
    }
    report = {}
    for key, url in urls.items():
        status, body = fetch(url)
        report[key] = {
            "status": status,
            "url": url,
            "body_preview": body[:800],
            "body_len": len(body),
        }
        if key == "sample_unfiltered" and status == 200:
            payload = json.loads(body)
            inds = sorted({row.get("Indicador") for row in payload.get("value") or []})
            report[key]["distinct_in_page"] = inds

    (OUT / "olinda-connectivity-diagnose.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: {"status": v["status"], "preview": v["body_preview"][:200], "extra": {ek: v[ek] for ek in v if ek.startswith("distinct")}} for k, v in report.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
