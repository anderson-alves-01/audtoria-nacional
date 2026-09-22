"""Copy minimized Trimestrais fixtures with ASCII filenames."""
from __future__ import annotations

import json
from pathlib import Path

SRC = Path("evidence/releases/0.3.93")
DST = Path("tests/fixtures/official-snapshots")

# probe stem (as written on disk) -> fixture stem
MAPPING = {
    "ipca": "ipca",
    "ipca-livres": "ipca-livres",
    "ipca-serviços": "ipca-servicos",
    "ipca-administrados": "ipca-administrados",
    "ipca-alimentação-no-domicílio": "ipca-alimentacao",
    "ipca-bens-industrializados": "ipca-bens-industrializados",
    "câmbio": "cambio",
    "pib-total": "pib-total",
}


def main() -> None:
    for probe_stem, fixture_stem in MAPPING.items():
        path = SRC / f"bcb-olinda-expectativas-{probe_stem}-trimestrais-bc1-top8-probe.json"
        if not path.exists():
            raise SystemExit(f"missing {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        slim = {"value": payload["value"]}
        dest = DST / f"bcb-olinda-expectativas-{fixture_stem}-trimestrais-top8.json"
        dest.write_text(
            json.dumps(slim, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        first = slim["value"][0]
        print(dest.name, first["Mediana"], first["DataReferencia"])


if __name__ == "__main__":
    main()
