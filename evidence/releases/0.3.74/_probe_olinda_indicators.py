"""Probe distinct BCB OLINDA ExpectativasMercadoAnuais indicators."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent
URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    "ExpectativasMercadoAnuais?$top=500&$format=json&"
    "$select=Indicador,IndicadorDetalhe,baseCalculo&$orderby=Data%20desc"
)
KNOWN = {
    "IPCA",
    "Selic",
    "Câmbio",
    "PIB Total",
    "PIB Serviços",
    "PIB Agropecuária",
    "PIB Indústria",
    "IGP-M",
    "IGP-DI",
    "INPC",
    "Dívida líquida do setor público",
    "Balança comercial",
    "Resultado primário",
    "Conta corrente",
    "Resultado nominal",
}


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "sirta-probe/0.3.74"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read()
    data = json.loads(body)
    rows = data.get("value") or []
    seen: dict[tuple, int] = {}
    for r in rows:
        key = (r.get("Indicador"), r.get("IndicadorDetalhe"), r.get("baseCalculo"))
        seen[key] = seen.get(key, 0) + 1
    lines = [
        f"# BCB OLINDA ExpectativasMercadoAnuais distinct indicators ({len(rows)} rows)",
        "",
    ]
    for k in sorted(seen, key=lambda x: (x[0] or "", x[1] or "", x[2] if x[2] is not None else -1)):
        flag = "KNOWN" if k[0] in KNOWN else "CANDIDATE"
        lines.append(f"{flag}\t{k[0]!r}\tdetalhe={k[1]!r}\tbase={k[2]}\tn={seen[k]}")
    out = EVIDENCE / "bcb-olinda-indicators-distinct.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
