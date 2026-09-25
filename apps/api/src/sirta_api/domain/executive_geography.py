"""Roll published municipal series into the five IBGE regions."""

from __future__ import annotations

EXECUTIVE_MAP_SOURCES = (
    "IBGE-SIDRA",
    "IBGE-SIDRA-PIB",
    "IBGE-SIDRA-CEMP",
)

SOURCE_LABELS = {
    "IBGE-SIDRA": "IBGE — população",
    "IBGE-SIDRA-PIB": "IBGE — PIB",
    "IBGE-SIDRA-CEMP": "IBGE — empresas",
}

UF_BY_CODE = {
    "11": ("RO", "Rondônia"),
    "12": ("AC", "Acre"),
    "13": ("AM", "Amazonas"),
    "14": ("RR", "Roraima"),
    "15": ("PA", "Pará"),
    "16": ("AP", "Amapá"),
    "17": ("TO", "Tocantins"),
    "21": ("MA", "Maranhão"),
    "22": ("PI", "Piauí"),
    "23": ("CE", "Ceará"),
    "24": ("RN", "Rio Grande do Norte"),
    "25": ("PB", "Paraíba"),
    "26": ("PE", "Pernambuco"),
    "27": ("AL", "Alagoas"),
    "28": ("SE", "Sergipe"),
    "29": ("BA", "Bahia"),
    "31": ("MG", "Minas Gerais"),
    "32": ("ES", "Espírito Santo"),
    "33": ("RJ", "Rio de Janeiro"),
    "35": ("SP", "São Paulo"),
    "41": ("PR", "Paraná"),
    "42": ("SC", "Santa Catarina"),
    "43": ("RS", "Rio Grande do Sul"),
    "50": ("MS", "Mato Grosso do Sul"),
    "51": ("MT", "Mato Grosso"),
    "52": ("GO", "Goiás"),
    "53": ("DF", "Distrito Federal"),
}

REGIONS = (
    ("norte", "Norte", ("11", "12", "13", "14", "15", "16", "17")),
    ("nordeste", "Nordeste", ("21", "22", "23", "24", "25", "26", "27", "28", "29")),
    ("centro-oeste", "Centro-Oeste", ("50", "51", "52", "53")),
    ("sudeste", "Sudeste", ("31", "32", "33", "35")),
    ("sul", "Sul", ("41", "42", "43")),
)

_REGION_BY_UF_CODE = {
    code: (region_id, region_name)
    for region_id, region_name, codes in REGIONS
    for code in codes
}


def region_for_ibge(ibge_code: str) -> tuple[str, str] | None:
    code = str(ibge_code or "").strip()
    if len(code) < 2:
        return None
    return _REGION_BY_UF_CODE.get(code[:2])


def aggregate_executive_geography(lines: list[dict]) -> dict:
    """Sum published municipal lines. A source with no line contributes nothing."""
    buckets: dict[tuple[str, str, str, str, str], dict] = {}
    for line in lines:
        source_id = str(line.get("sourceId") or "")
        if source_id not in EXECUTIVE_MAP_SOURCES:
            continue
        ibge = str(line.get("ibgeCode") or "").strip()
        if region_for_ibge(ibge) is None or not isinstance(line.get("value"), (int, float)):
            continue
        label = str(line.get("variableName") or SOURCE_LABELS[source_id]).strip()
        unit = str(line.get("unit") or "UNIT").strip() or "UNIT"
        competence = str(line.get("competence") or "")[:4]
        key = (ibge[:2], source_id, label, unit, competence)
        bucket = buckets.setdefault(key, {"total": 0.0, "municipalities": set()})
        bucket["total"] += float(line["value"])
        bucket["municipalities"].add(ibge)
    groups = [
        {
            "sourceId": source_id,
            "ufCode": uf_code,
            "label": label,
            "unit": unit,
            "competence": competence,
            "total": bucket["total"],
            "municipalityCount": len(bucket["municipalities"]),
        }
        for (uf_code, source_id, label, unit, competence), bucket in buckets.items()
    ]
    return assemble_geography(groups)


def assemble_geography(groups: list[dict]) -> dict:
    states: dict[str, dict] = {}
    for group in groups:
        uf_code = str(group.get("ufCode") or "")
        source_id = str(group.get("sourceId") or "")
        if uf_code not in UF_BY_CODE or source_id not in EXECUTIVE_MAP_SOURCES:
            continue
        region_id, _region_name = _REGION_BY_UF_CODE[uf_code]
        uf, uf_name = UF_BY_CODE[uf_code]
        state = states.setdefault(
            uf,
            {"uf": uf, "name": uf_name, "regionId": region_id, "measures": []},
        )
        state["measures"].append(
            {
                "sourceId": source_id,
                "sourceLabel": SOURCE_LABELS[source_id],
                "label": str(group.get("label") or SOURCE_LABELS[source_id]),
                "unit": str(group.get("unit") or "UNIT"),
                "competence": str(group.get("competence") or "")[:4],
                "total": round(float(group["total"]), 4),
                "municipalityCount": int(group.get("municipalityCount") or 0),
            }
        )

    regions = []
    for region_id, region_name, codes in REGIONS:
        region_states = []
        for code in codes:
            uf, uf_name = UF_BY_CODE[code]
            region_states.append(
                states.get(
                    uf,
                    {"uf": uf, "name": uf_name, "regionId": region_id, "measures": []},
                )
            )
        regions.append(
            {
                "id": region_id,
                "name": region_name,
                "states": region_states,
            }
        )
    return {"createsTaxCredit": False, "regions": regions}
