"""Probe OLINDA ExpectativasMercadoAnuais for distinct Indicador values."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import Counter
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

CANDIDATES = [
    # inflation / prices
    "IGP-10",
    "IPA",
    "IPC-Br",
    "IPC",
    "INCC-M",
    "INCC-DI",
    "INCC",
    "IPCA Alimentação e bebidas",
    "IPCA Habitação",
    "IPCA Artigos de residência",
    "IPCA Vestuário",
    "IPCA Transportes",
    "IPCA Saúde e cuidados pessoais",
    "IPCA Despesas pessoais",
    "IPCA Educação",
    "IPCA Comunicação",
    # growth / activity
    "PIB",
    "Crescimento do PIB",
    "Produção Industrial",
    "Meta para inflação",
    # rates / FX
    "Taxa de câmbio",
    "Taxa Selic",
    "Selic meta",
    "TJLP",
    "TR",
    # fiscal / external
    "Resultado primário do governo central",
    "Dívida líquida",
    "Dívida bruta",
    "Investimento direto",
    "Investimentos diretos no país",
    "Conta-corrente",
    "Saldo em conta corrente",
    "Balança Comercial",
    "Exportações",
    "Importações",
    # labor
    "Desemprego",
    "Taxa de desemprego",
    "População desocupada",
    # commodities / energy (sometimes in Focus)
    "Preço do petróleo",
    "Petróleo",
]


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "sirta-probe/0.3.88"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe_indicator(name: str, base_calculo: int = 1, detalhe: str | None = None) -> dict:
    filt = f"Indicador eq '{name}' and baseCalculo eq {base_calculo}"
    if detalhe:
        filt += f" and IndicadorDetalhe eq '{detalhe}'"
    params = {
        "$top": "2",
        "$format": "json",
        "$filter": filt,
        "$orderby": "Data desc,DataReferencia asc",
        "$select": "Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo",
    }
    url = BASE + "ExpectativasMercadoAnuais?" + urllib.parse.urlencode(params)
    try:
        payload = fetch(url)
        rows = payload.get("value") or []
        return {
            "indicator": name,
            "baseCalculo": base_calculo,
            "detalhe": detalhe,
            "count": len(rows),
            "sample": rows[:2],
            "url": url,
            "ok": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "indicator": name,
            "baseCalculo": base_calculo,
            "detalhe": detalhe,
            "count": 0,
            "error": str(exc),
            "url": url,
            "ok": False,
        }


def main() -> None:
    results = []
    found = []
    for name in CANDIDATES:
        if name in KNOWN:
            continue
        for base in (1, 0):
            r = probe_indicator(name, base)
            results.append(r)
            if r.get("count", 0) > 0:
                found.append(r)
                break

    # Also verify a known one still works
    sanity = probe_indicator("IPCA", 1)
    summary = {
        "known_count": len(KNOWN),
        "candidates_probed": len(CANDIDATES),
        "found_new": [
            {
                "indicator": r["indicator"],
                "baseCalculo": r["baseCalculo"],
                "median": (r["sample"][0].get("Mediana") if r["sample"] else None),
                "data": (r["sample"][0].get("Data") if r["sample"] else None),
                "detalhe": (r["sample"][0].get("IndicadorDetalhe") if r["sample"] else None),
            }
            for r in found
        ],
        "sanity_ipca_count": sanity.get("count"),
        "hits": len(found),
    }
    (OUT / "olinda-remaining-name-probe.json").write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
