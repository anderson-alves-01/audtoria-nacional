"""Streaming RFB Estabelecimentos parser with territorial filter and EI policy."""

from __future__ import annotations

import csv
import io

from sirta_api.domain.rfb_cnpj import (
    ResumeCursor,
    TerritorialScope,
    ei_policy_decision,
    next_resume_plan,
)

# Positional layout from RFB LAYOUT_DADOS_ABERTOS_CNPJ (Estabelecimentos).
_UF_INDEX = 19
_MUNICIPIO_RFB_INDEX = 20
_CNPJ_BASICO = 0
_CNPJ_ORDEM = 1
_CNPJ_DV = 2
_CNAE = 11


def parse_municipios_lookup(body: bytes) -> dict[str, str]:
    """Map RFB municipio code -> name from Municipios.zip CSV (codigo;nome)."""
    text = body.decode("latin-1")
    lookup: dict[str, str] = {}
    for row in csv.reader(io.StringIO(text), delimiter=";"):
        if len(row) < 2:
            continue
        code = str(row[0]).strip()
        name = str(row[1]).strip()
        if code:
            lookup[code] = name
    return lookup


def parse_rfb_estabelecimentos(
    body: bytes,
    *,
    scope: TerritorialScope,
    nature_by_cnpj_basico: dict[str, str] | None = None,
    rfb_to_ibge: dict[str, str] | None = None,
    minimize_individual_entrepreneur: bool = True,
    resume_byte_offset: int = 0,
) -> tuple[list[dict], list[tuple[dict, str]], int]:
    """Parse minimized Estabelecimentos CSV bytes.

    Returns silver rows, quarantined pairs and next byte offset for resume.
    """
    natures = nature_by_cnpj_basico or {}
    ibge_map = rfb_to_ibge or {}
    if resume_byte_offset:
        raw = body[resume_byte_offset:]
    else:
        raw = body
    text = raw.decode("latin-1")
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    consumed = resume_byte_offset
    for line in text.splitlines(keepends=True):
        line_bytes = line.encode("latin-1")
        consumed += len(line_bytes)
        row = next(csv.reader(io.StringIO(line), delimiter=";"), [])
        if not row:
            continue
        if len(row) <= _MUNICIPIO_RFB_INDEX:
            quarantined.append(({"rowId": "short-row"}, "incomplete_estabelecimento_row"))
            continue
        uf = str(row[_UF_INDEX]).strip().upper()
        rfb_mun = str(row[_MUNICIPIO_RFB_INDEX]).strip()
        if scope.ufs and uf not in scope.ufs:
            continue
        if scope.rfb_municipio_codes and rfb_mun not in scope.rfb_municipio_codes:
            continue
        ibge = ibge_map.get(rfb_mun, "")
        if scope.ibge_codes and ibge not in scope.ibge_codes:
            continue
        basico = str(row[_CNPJ_BASICO]).strip()
        ordem = str(row[_CNPJ_ORDEM]).strip()
        dv = str(row[_CNPJ_DV]).strip()
        cnae = str(row[_CNAE]).strip() if len(row) > _CNAE else ""
        natureza = natures.get(basico)
        payload = {
            "rowId": f"rfb-{basico}{ordem}{dv}"[:64],
            "cnpjBasico": basico,
            "uf": uf,
            "rfbMunicipioCode": rfb_mun,
            "ibgeCode": ibge or None,
            "cnaeFiscal": cnae or None,
            "naturezaJuridica": natureza,
        }
        reason = ei_policy_decision(
            natureza_codigo=natureza,
            minimize_individual_entrepreneur=minimize_individual_entrepreneur,
        )
        if reason:
            quarantined.append((payload, reason))
            continue
        silver.append(payload)
    return silver, quarantined, consumed


def plan_rfb_resume(cursor_raw: str | None = None) -> str:
    decoded = ResumeCursor.decode(cursor_raw)
    planned = next_resume_plan(cursor=decoded)
    return planned.encode()
