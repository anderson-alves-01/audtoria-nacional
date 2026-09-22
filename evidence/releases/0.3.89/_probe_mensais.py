import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("evidence/releases/0.3.89")
BASE = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"

def fetch(path: str) -> dict:
    url = BASE + path
    with urllib.request.urlopen(url, timeout=90) as resp:
        return json.load(resp)

indicators = [
    "IPCA", "IGP-M", "IGP-DI", "INPC", "IPC-Fipe", "IPCA-15",
    "Câmbio", "Selic", "IPA-M", "IPA-DI", "IPCA Livres", "IPCA Serviços",
    "IPCA Administrados", "IPCA Alimentação no domicílio",
    "IPCA Bens industrializados", "Meta para inflação",
]
hits = []
for ind in indicators:
    for bc in (0, 1):
        filt = urllib.parse.quote(f"Indicador eq '{ind}' and baseCalculo eq {bc}", safe="")
        path = (
            "ExpectativaMercadoMensais?$top=8&$format=json&"
            f"$filter={filt}&$orderby=Data%20desc,DataReferencia%20asc&"
            "$select=Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
        )
        try:
            data = fetch(path)
            rows = data.get("value") or []
            entry = {
                "indicator": ind,
                "baseCalculo": bc,
                "count": len(rows),
                "ok": True,
                "sample": rows[:3],
                "url": BASE + path,
            }
            if rows:
                hits.append(entry)
                slug = ind.lower().replace(" ", "-").replace("â", "a").replace("ç", "c").replace("ã", "a")
                slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
                (OUT / f"bcb-olinda-expectativas-{slug}-mensais-bc{bc}-top8-probe.json").write_text(
                    json.dumps({"value": rows}, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(f"HIT {ind} bc={bc} n={len(rows)} data={rows[0].get('Data')} ref={rows[0].get('DataReferencia')} med={rows[0].get('Mediana')}")
            else:
                print(f"EMPTY {ind} bc={bc}")
        except Exception as exc:
            print(f"ERR {ind} bc={bc}: {exc}")

# Discover distinct indicators via paging recent rows
seen = {}
for page in range(0, 20):
    skip = page * 100
    path = (
        f"ExpectativaMercadoMensais?$top=100&$skip={skip}&$format=json&"
        "$orderby=Data%20desc&$select=Indicador,baseCalculo"
    )
    try:
        data = fetch(path)
    except Exception as exc:
        print(f"page {page} err: {exc}")
        break
    rows = data.get("value") or []
    if not rows:
        break
    for row in rows:
        key = (row.get("Indicador"), row.get("baseCalculo"))
        seen[key] = seen.get(key, 0) + 1
    print(f"page {page}: rows={len(rows)} distinct_so_far={len(seen)}")

summary = {
    "hits": [
        {
            "indicator": h["indicator"],
            "baseCalculo": h["baseCalculo"],
            "count": h["count"],
            "data": (h["sample"][0] or {}).get("Data") if h["sample"] else None,
            "mediana": (h["sample"][0] or {}).get("Mediana") if h["sample"] else None,
            "dataReferencia": (h["sample"][0] or {}).get("DataReferencia") if h["sample"] else None,
        }
        for h in hits
    ],
    "distinct_pairs": [
        {"Indicador": k[0], "baseCalculo": k[1], "n": v}
        for k, v in sorted(seen.items(), key=lambda x: (-x[1], str(x[0]), x[1]))
    ],
}
(OUT / "olinda-mensais-discovery.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("DONE distinct=", len(seen), "hits=", len(hits))
