"""Baixa uma vez a lista oficial de municípios do IBGE e grava um JSON versionado.

Dado público de referência territorial, sem dado fiscal. Somente leitura na rede, uma chamada.
O Simulador usa o arquivo gerado e não chama o IBGE em execução.

Uso:
    python tools/ops/ibge-municipios-fetch.py            # baixa, grava o JSON e a evidência
    python tools/ops/ibge-municipios-fetch.py --verify   # só confere o JSON e o sha256 gravados
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "apps" / "web" / "public" / "ibge-municipios.json"
EVIDENCE = ROOT / "evidence" / "ops" / "ibge-municipios-20261028.txt"
EXPECTED_UFS = 27


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalise(payload: list[dict]) -> list[dict]:
    rows = []
    for item in payload:
        uf = (
            item["microrregiao"]["mesorregiao"]["UF"]["sigla"]
            if item.get("microrregiao")
            else (item["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"])
        )
        rows.append({"uf": uf, "ibge": str(item["id"]), "nome": item["nome"]})
    rows.sort(key=lambda row: (row["uf"], row["nome"]))
    return rows


def _check(rows: list[dict]) -> list[str]:
    problems = []
    if len({row["uf"] for row in rows}) != EXPECTED_UFS:
        problems.append("a lista não cobre as 27 UFs")
    if len({row["ibge"] for row in rows}) != len(rows):
        problems.append("código IBGE repetido")
    if any(len(row["ibge"]) != 7 or not row["ibge"].isdigit() for row in rows):
        problems.append("código IBGE fora do formato de 7 dígitos")
    return problems


def verify() -> int:
    data = OUTPUT.read_bytes()
    document = json.loads(data)
    problems = _check(document["municipios"])
    print(f"municipios={len(document['municipios'])} sha256={_sha256(data)}")
    for problem in problems:
        print(f"FALHA {problem}")
    return 1 if problems else 0


def fetch() -> int:
    request = urllib.request.Request(URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (URL fixa, https)
        raw = response.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    rows = _normalise(json.loads(raw))
    problems = _check(rows)
    if problems:
        for problem in problems:
            print(f"FALHA {problem}")
        return 1
    document = {
        "fonte": URL,
        "obtidoEm": datetime.now(UTC).strftime("%Y-%m-%d"),
        "sha256Resposta": _sha256(raw),
        "total": len(rows),
        "aviso": "Lista territorial de referência. Não contém dado fiscal nem alíquota.",
        "municipios": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(document, ensure_ascii=False, indent=0) + "\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    EVIDENCE.write_text(
        "\n".join(
            [
                "Lista de municípios do IBGE (referência territorial, sem dado fiscal)",
                f"Fonte: {URL}",
                f"Obtida em: {document['obtidoEm']} (uma chamada, sem credencial)",
                f"Municípios: {len(rows)} em {EXPECTED_UFS} UFs",
                f"sha256 da resposta: {document['sha256Resposta']}",
                f"sha256 do arquivo gravado: {_sha256(encoded)}",
                "Arquivo: apps/web/public/ibge-municipios.json",
                "Conferência: python tools/ops/ibge-municipios-fetch.py --verify",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"municipios={len(rows)} sha256={_sha256(encoded)}")
    return 0


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else fetch())
