"""Tax Better intake and the general vision.

Amounts arrive from an organ file. This module groups them. It does not
derive a tax from a rate, and it does not approve a malha export.
"""

import csv
import io
from decimal import Decimal, InvalidOperation

TAXES = ("ICMS", "ISS", "IPTU", "IPVA", "ITBI", "ITCMD")

ORGANS = ({"code": "DETRAN", "name": "DETRAN"},)

FGOS = (
    {
        "code": "VENDA_PJ",
        "label": "VENDA PJ",
        "tax": "ICMS",
        "organ": "DETRAN",
        "pdfItem": "3.2.1a",
    },
    {
        "code": "VENDA_SOCIO",
        "label": "VENDA SOCIO",
        "tax": "ICMS",
        "organ": "DETRAN",
        "pdfItem": "3.2.1b",
    },
    {
        "code": "VENDA_PF",
        "label": "VENDA PF",
        "tax": "ICMS",
        "organ": "DETRAN",
        "pdfItem": "3.2.1c",
    },
    {
        "code": "VENDA_PJ_BASE",
        "label": "VENDA PJ BASE",
        "tax": "ICMS",
        "organ": "DETRAN",
        "pdfItem": "3.2.1d",
    },
    {
        "code": "DIFAL_USO",
        "label": "DIFAL USO",
        "tax": "ICMS",
        "organ": None,
        "pdfItem": "3.2.1e",
    },
    {
        "code": "COMPRA_MAIOR",
        "label": "COMPRA MAIOR QUE VENDA",
        "tax": "ICMS",
        "organ": None,
        "pdfItem": "3.2.1f",
    },
    {
        "code": "MATERIAL_OBRA",
        "label": "MATERIAL FORA DO LOCAL",
        "tax": "ICMS",
        "organ": None,
        "pdfItem": "3.2.1g",
    },
    {
        "code": "DIFAL_MATERIAL",
        "label": "DIFAL MATERIAL",
        "tax": "ICMS",
        "organ": None,
        "pdfItem": "3.2.1h",
    },
)

_EMPTY = {"valor": None, "baseCalculo": None, "imposto": None}


def support_catalog() -> dict:
    return {
        "taxes": [{"code": code} for code in TAXES],
        "organs": [dict(item) for item in ORGANS],
        "fgos": [dict(item) for item in FGOS],
    }


def receive_lines(lines: list[dict]) -> dict:
    """Group an organ file into the general vision."""
    known = {item["label"]: item for item in FGOS}
    grouped: dict[tuple, dict] = {}
    for line in lines:
        organ = str(line.get("organ", "")).strip()
        tax = line.get("tax")
        label = line.get("fgo")
        fgo = known.get(label)
        if not organ or tax not in TAXES or fgo is None or fgo["tax"] != tax:
            raise ValueError("Linha recusada: órgão, imposto ou fato gerador.")
        variables = {
            str(key): str(value)
            for key, value in dict(line.get("variables") or {}).items()
        }
        key = (tax, label, tuple(sorted(variables.items())))
        bucket = grouped.setdefault(
            key,
            {"operacao": dict(_EMPTY), "malha": dict(_EMPTY)},
        )
        _add(bucket["operacao"], "valor", line.get("operationValue"))
        _add(bucket["operacao"], "baseCalculo", line.get("operationBase"))
        _add(bucket["operacao"], "imposto", line.get("operationTax"))
        _add(bucket["malha"], "valor", line.get("malhaValue"))
        _add(bucket["malha"], "baseCalculo", line.get("malhaBase"))
        _add(bucket["malha"], "imposto", line.get("malhaTax"))
    rows = []
    for (tax, label, pairs), measures in grouped.items():
        rows.append(
            {
                "imposto": tax,
                "fgo": label,
                "variables": dict(pairs),
                "operacao": measures["operacao"],
                "malha": measures["malha"],
                "approved": False,
            }
        )
    return {"createsTaxCredit": False, "rows": rows}


def fgo_code(label: str) -> str:
    for item in FGOS:
        if item["label"] == label:
            return item["code"]
    raise IntakeConfigError("Fato gerador sem código de apoio.")


def fgo_label(code: str) -> str:
    for item in FGOS:
        if item["code"] == code:
            return item["label"]
    raise IntakeConfigError("Fato gerador sem código de apoio.")


EMPTY_VISION = "Ainda não há arquivo autorizado na visão."


def vision_from_stored(lines: list[dict]) -> dict:
    """Group lines already stored. Does not invent a measure or approve an export."""
    if not lines:
        return {
            "createsTaxCredit": False,
            "approvedExport": False,
            "emptyReason": EMPTY_VISION,
            "rows": [],
        }
    vision = receive_lines(lines)
    return {
        "createsTaxCredit": False,
        "approvedExport": False,
        "emptyReason": None,
        "rows": [_public_row(row) for row in vision["rows"]],
    }


def _public_row(row: dict) -> dict:
    return {
        "imposto": row["imposto"],
        "fgo": row["fgo"],
        "variables": row["variables"],
        "operacao": _plain_side(row["operacao"]),
        "malha": _plain_side(row["malha"]),
        "approved": False,
    }


def _plain_side(side: dict) -> dict:
    return {
        key: None if side.get(key) is None else str(side[key])
        for key in ("valor", "baseCalculo", "imposto")
    }


MAP_FIELDS = (
    "organ",
    "tax",
    "fgo",
    "operationValue",
    "operationBase",
    "operationTax",
    "malhaValue",
    "malhaBase",
    "malhaTax",
)
_AMOUNT_FIELDS = {
    "operationValue",
    "operationBase",
    "operationTax",
    "malhaValue",
    "malhaBase",
    "malhaTax",
}


class IntakeConfigError(ValueError):
    pass


def read_configured_intake(
    config: dict,
    *,
    file_text: str | None = None,
    api_rows: list[dict] | None = None,
) -> dict:
    """Read a file or an API body through the same field map. Does not call a URL."""
    channel = config.get("channel")
    field_map = dict(config.get("fieldMap") or {})
    if channel not in {"file", "api"} or any(
        not str(field_map.get(key) or "").strip() for key in MAP_FIELDS
    ):
        raise IntakeConfigError("Leiaute incompleto: canal e mapa de campos são obrigatórios.")
    if "secret" in config or "secretValue" in config:
        raise IntakeConfigError("O segredo não é gravado. Informe só o nome.")
    if channel == "api" and not str(config.get("secretName") or "").strip():
        raise IntakeConfigError("API sem nome de segredo configurado.")
    raw_rows = _raw_rows(channel, file_text=file_text, api_rows=api_rows)
    accepted: list[dict] = []
    quarantined: list[dict] = []
    known = {item["label"]: item for item in FGOS}
    for index, raw in enumerate(raw_rows, start=1):
        line = _project(raw, field_map)
        fgo = known.get(line["fgo"])
        if line["missing"] or not line["organ"] or line["tax"] not in TAXES or fgo is None:
            quarantined.append({"row": index, "reason": "campo obrigatório ausente"})
            continue
        if fgo["tax"] != line["tax"]:
            quarantined.append({"row": index, "reason": "campo obrigatório ausente"})
            continue
        accepted.append(
            {
                "organ": line["organ"],
                "tax": line["tax"],
                "fgo": line["fgo"],
                "variables": line["variables"],
                "operationValue": line["operationValue"],
                "operationBase": line["operationBase"],
                "operationTax": line["operationTax"],
                "malhaValue": line["malhaValue"],
                "malhaBase": line["malhaBase"],
                "malhaTax": line["malhaTax"],
                "approved": False,
            }
        )
    vision = receive_lines(accepted) if accepted else {"createsTaxCredit": False, "rows": []}
    return {
        "createsTaxCredit": False,
        "accepted": accepted,
        "quarantined": quarantined,
        "vision": vision,
    }


def _raw_rows(channel: str, *, file_text: str | None, api_rows: list[dict] | None) -> list[dict]:
    if channel == "file":
        reader = csv.DictReader(io.StringIO(file_text or ""))
        return [dict(row) for row in reader]
    return [dict(row) for row in (api_rows or [])]


def _project(raw: dict, field_map: dict) -> dict:
    used = {str(field_map[key]) for key in MAP_FIELDS}
    values = {key: str(raw.get(field_map[key]) or "").strip() for key in MAP_FIELDS}
    missing = any(values[key] == "" for key in MAP_FIELDS)
    variables = {
        str(key): str(value).strip()
        for key, value in raw.items()
        if str(key) not in used and str(value).strip()
    }
    projected = {
        "organ": values["organ"],
        "tax": values["tax"],
        "fgo": values["fgo"],
        "variables": variables,
        "missing": missing,
    }
    for key in _AMOUNT_FIELDS:
        if values[key] == "":
            projected[key] = None
            continue
        try:
            projected[key] = Decimal(values[key])
        except InvalidOperation:
            projected[key] = None
            projected["missing"] = True
    return projected


def _add(side: dict, field: str, incoming) -> None:
    if incoming is None:
        return
    amount = Decimal(incoming)
    current = side[field]
    side[field] = amount if current is None else current + amount
