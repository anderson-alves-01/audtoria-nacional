"""Discover remaining OLINDA Focus annual indicators / detalhes."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"

KNOWN = {
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
    "PIB Formação Bruta de Capital Fixo",
    "PIB Despesa de consumo das famílias",
    "PIB Despesa de consumo da administração pública",
    "PIB Exportação de bens e serviços",
    "PIB Importação de bens e serviços",
    "Produção industrial",
    "IPCA-15",
    "IPC-Fipe",
    "IPA-M",
    "IPA-DI",
    "IGP-M",
    "IGP-DI",
    "INPC",
    "Dívida líquida do setor público",
    "Dívida bruta do governo geral",
    "Balança comercial",
    "Resultado primário",
    "Conta corrente",
    "Resultado nominal",
    "Taxa de desocupação",
    "Investimento direto no país",
}

KNOWN_DETALHE = {("Balança comercial", "Saldo")}

CANDIDATES = [
    "IGP-10",
    "IPA",
    "IPC-Br",
    "INCC-M",
    "INCC-DI",
    "INCC",
    "IPCA Habitação",
    "IPCA Transportes",
    "IPCA Educação",
    "IPCA Comunicação",
    "IPCA Vestuário",
    "Meta para inflação",
    "Produção Industrial",
    "Exportações",
    "Importações",
    "PIB",
    "TJLP",
    "TR",
]


def build_url(params: dict) -> str:
    # OLINDA is picky: prefer %20 over +
    return BASE + "ExpectativasMercadoAnuais?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.88"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe(name: str, base: int = 1, detalhe: str | None = None, select_detalhe: bool = False) -> dict:
    filt = f"Indicador eq '{name}' and baseCalculo eq {base}"
    if detalhe is not None:
        filt += f" and IndicadorDetalhe eq '{detalhe}'"
    select = "Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    if select_detalhe or detalhe is not None:
        select = "Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    params = {
        "$top": "8",
        "$format": "json",
        "$filter": filt,
        "$orderby": "Data desc,DataReferencia asc",
        "$select": select,
    }
    url = build_url(params)
    try:
        payload = fetch(url)
        rows = payload.get("value") or []
        return {
            "indicator": name,
            "baseCalculo": base,
            "detalhe": detalhe,
            "count": len(rows),
            "sample": rows[:3],
            "url": url,
            "ok": True,
        }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:400]
        return {
            "indicator": name,
            "baseCalculo": base,
            "detalhe": detalhe,
            "count": 0,
            "error": f"HTTP {exc.code}: {body}",
            "url": url,
            "ok": False,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "indicator": name,
            "baseCalculo": base,
            "detalhe": detalhe,
            "count": 0,
            "error": repr(exc),
            "url": url,
            "ok": False,
        }


def page_distinct(max_pages: int = 40, page_size: int = 100) -> dict:
    """Collect distinct Indicador (+optional detalhe) via skip pagination."""
    counts: dict[tuple, int] = defaultdict(int)
    pages = []
    for page in range(max_pages):
        skip = page * page_size
        params = {
            "$top": str(page_size),
            "$skip": str(skip),
            "$format": "json",
            "$select": "Indicador,IndicadorDetalhe,baseCalculo",
            "$orderby": "Indicador,IndicadorDetalhe,baseCalculo",
        }
        url = build_url(params)
        try:
            payload = fetch(url)
        except Exception as exc:  # noqa: BLE001
            pages.append({"page": page, "error": repr(exc), "url": url})
            break
        rows = payload.get("value") or []
        pages.append({"page": page, "rows": len(rows)})
        if not rows:
            break
        for row in rows:
            key = (row.get("Indicador"), row.get("IndicadorDetalhe"), row.get("baseCalculo"))
            counts[key] += 1
        if len(rows) < page_size:
            break
    return {
        "pages": pages,
        "pairs": [
            {"Indicador": k[0], "IndicadorDetalhe": k[1], "baseCalculo": k[2], "n": n}
            for k, n in sorted(counts.items(), key=lambda x: (x[0][0] or "", x[0][1] or "", x[0][2] or 0))
        ],
    }


def main() -> None:
    sanity = probe("IPCA", 1)
    found = []
    results = [sanity]
    for name in CANDIDATES:
        if name in KNOWN:
            continue
        hit = None
        for base in (1, 0):
            r = probe(name, base)
            results.append(r)
            if r.get("count", 0) > 0:
                hit = r
                break
        if hit:
            found.append(hit)

    # Balança detalhes not yet allowlisted
    balanca = []
    for detalhe in ("Exportações", "Importações", "Saldo"):
        for base in (1, 0):
            r = probe("Balança comercial", base, detalhe=detalhe, select_detalhe=True)
            results.append(r)
            balanca.append(r)

    distinct = page_distinct()
    known_names = set(KNOWN)
    distinct_names = {p["Indicador"] for p in distinct["pairs"]}
    missing = sorted(distinct_names - known_names)
    missing_detalhe = [
        p
        for p in distinct["pairs"]
        if p["Indicador"] == "Balança comercial"
        and (p["Indicador"], p["IndicadorDetalhe"]) not in KNOWN_DETALHE
        and p["IndicadorDetalhe"] is not None
    ]

    summary = {
        "sanity_ipca": {
            "ok": sanity.get("ok"),
            "count": sanity.get("count"),
            "median": (sanity.get("sample") or [{}])[0].get("Mediana"),
            "error": sanity.get("error"),
        },
        "found_new_indicators": [
            {
                "indicator": r["indicator"],
                "baseCalculo": r["baseCalculo"],
                "median": (r.get("sample") or [{}])[0].get("Mediana"),
                "data": (r.get("sample") or [{}])[0].get("Data"),
            }
            for r in found
        ],
        "balanca_hits": [
            {
                "detalhe": r["detalhe"],
                "baseCalculo": r["baseCalculo"],
                "count": r["count"],
                "median": (r.get("sample") or [{}])[0].get("Mediana") if r.get("sample") else None,
                "data": (r.get("sample") or [{}])[0].get("Data") if r.get("sample") else None,
            }
            for r in balanca
            if r.get("count", 0) > 0
        ],
        "distinct_names_count": len(distinct_names),
        "missing_from_allowlist": missing,
        "balanca_detalhe_variants": missing_detalhe[:20],
        "distinct_pairs_count": len(distinct["pairs"]),
    }

    (OUT / "olinda-discovery-summary.json").write_text(
        json.dumps(
            {"summary": summary, "distinct": distinct, "results": results},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    # also save compact top8 fixtures for balanca export/import if present
    for detalhe, slug in (("Exportações", "exportacoes"), ("Importações", "importacoes")):
        r = probe("Balança comercial", 1, detalhe=detalhe, select_detalhe=True)
        if r.get("count", 0) > 0:
            payload = {"value": r["sample"]}
            # refetch full top8 for fixture
            full = probe("Balança comercial", 1, detalhe=detalhe, select_detalhe=True)
            # need actual full payload - re-fetch
            url = full["url"]
            full_payload = fetch(url)
            (OUT / f"bcb-olinda-expectativas-balanca-{slug}-anuais-top8-probe.json").write_text(
                json.dumps(full_payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
