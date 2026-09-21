from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

IBGE_MUNICIPALITY = re.compile(r"^\d{7}$")
PERSONAL_KEYS = frozenset({"cnpj", "cpf", "nome_empresario", "email", "telefone"})


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_ibge_sidra_series(body: bytes) -> tuple[list[dict], list[tuple[dict, str]]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "document"}, "invalid JSON")]
    if not isinstance(payload, list):
        return [], [({"rowId": "document"}, "unexpected SIDRA envelope")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for variable in payload:
        var_id = str(variable.get("id") or "")
        var_name = str(variable.get("variavel") or "")
        unit = str(variable.get("unidade") or "")
        for result in variable.get("resultados") or []:
            for series in result.get("series") or []:
                locality = series.get("localidade") or {}
                ibge_code = str(locality.get("id") or "")
                name = str(locality.get("nome") or "")
                level = str((locality.get("nivel") or {}).get("id") or "")
                values = series.get("serie") or {}
                if not values:
                    quarantined.append(
                        ({"rowId": ibge_code or "unknown", "ibgeCode": ibge_code}, "missing series")
                    )
                    continue
                for competence, raw in values.items():
                    row = {
                        "rowId": f"{var_id}-{ibge_code}-{competence}",
                        "ibgeCode": ibge_code,
                        "territoryName": name,
                        "territorialLevel": level,
                        "variableId": var_id,
                        "variableName": var_name,
                        "unit": unit,
                        "competence": str(competence),
                        "value": raw,
                    }
                    ok, reason = _sidra_row_valid(row)
                    if ok:
                        silver.append({**row, "value": float(str(raw).replace(",", "."))})
                    else:
                        quarantined.append((row, reason or "invalid SIDRA row"))
    return silver, quarantined


def _sidra_row_valid(row: dict) -> tuple[bool, str | None]:
    competence = str(row.get("competence") or "")
    if not re.fullmatch(r"\d{4}", competence):
        return False, "invalid competence"
    if str(row.get("territorialLevel") or "") == "N6" and not IBGE_MUNICIPALITY.fullmatch(
        str(row.get("ibgeCode") or "")
    ):
        return False, "invalid IBGE municipality code"
    if not str(row.get("ibgeCode") or ""):
        return False, "missing territorial code"
    raw = row.get("value")
    if raw in (None, "", "...", "-", "X"):
        return False, "missing value"
    try:
        value = float(str(raw).replace(",", "."))
    except ValueError:
        return False, "non numeric value"
    if value < 0:
        return False, "negative value"
    return True, None


def parse_siconfi_entes(body: bytes) -> tuple[list[dict], list[tuple[dict, str]]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "document"}, "invalid JSON")]
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return [], [({"rowId": "document"}, "unexpected SICONFI envelope")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for item in items:
        raw_code = str(item.get("cod_ibge") or "").strip()
        esfera = str(item.get("esfera") or "").strip()
        name = str(item.get("ente") or "").strip()
        uf = str(item.get("uf") or "").strip()
        competence = str(item.get("exercicio") or "").strip()
        population = item.get("populacao")
        row = {
            "rowId": f"{raw_code}-{competence}",
            "ibgeCode": raw_code,
            "territoryName": name,
            "uf": uf,
            "esfera": esfera,
            "competence": competence,
            "value": population,
            "unit": "Pessoas",
        }
        if esfera != "M":
            continue
        if not IBGE_MUNICIPALITY.fullmatch(raw_code):
            quarantined.append((row, "invalid IBGE municipality code"))
            continue
        if not re.fullmatch(r"\d{4}", competence):
            quarantined.append((row, "invalid competence"))
            continue
        try:
            value = float(population)
        except (TypeError, ValueError):
            quarantined.append((row, "non numeric population"))
            continue
        if value < 0:
            quarantined.append((row, "negative value"))
            continue
        silver.append({**row, "value": value})
    return silver, quarantined


def parse_tesouro_transfer_types(body: bytes) -> tuple[list[dict], list[tuple[dict, str]]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "document"}, "invalid JSON")]
    registros = payload.get("registros") if isinstance(payload, dict) else None
    if not isinstance(registros, list):
        return [], [({"rowId": "document"}, "unexpected Tesouro envelope")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for item in registros:
        code = item.get("codigo")
        name = str(item.get("transferencia") or "").strip()
        row = {
            "rowId": str(code),
            "transferCode": code,
            "transferName": name,
            "competence": "as_published",
            "value": 1,
            "unit": "tipo",
        }
        if not name or code is None:
            quarantined.append((row, "missing transfer type"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_official_document(
    body: bytes, *, content_type: str | None, url: str
) -> tuple[list[dict], list[tuple[dict, str]]]:
    if not body:
        return [], [({"rowId": "document"}, "empty document")]
    text_sample = body[:200].decode("utf-8", errors="replace").lower()
    if "html" not in (content_type or "").lower() and "<html" not in text_sample:
        return [], [({"rowId": "document"}, "unexpected document type")]
    silver = [
        {
            "rowId": sha256_bytes(body),
            "documentUrl": url,
            "bytes": len(body),
            "contentType": content_type or "application/octet-stream",
            "competence": "as_published",
            "value": 1,
            "unit": "document",
            "binding": False,
            "operational": False,
            "homologated": False,
            "status": "NON_BINDING",
        }
    ]
    return silver, []


def landing_dir(
    *, root: Path, source_id: str, dataset: str, extracted_at: datetime, checksum: str
) -> Path:
    day = extracted_at.astimezone(UTC).strftime("%Y-%m-%d")
    return root / "landing" / source_id / dataset / day / checksum


def write_landing(*, directory: Path, body: bytes, manifest: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    payload_path = directory / "payload.bin"
    if payload_path.exists():
        existing = sha256_bytes(payload_path.read_bytes())
        if existing != manifest["sha256"]:
            raise FileExistsError("landing payload would be overwritten with a different checksum")
        return
    payload_path.write_bytes(body)
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def minimize_row(row: dict) -> dict:
    return {key: value for key, value in row.items() if key.lower() not in PERSONAL_KEYS}


def normalize_place(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", ascii_only).strip().upper()


def parse_brazilian_number(raw: object) -> float:
    text = str(raw or "").strip()
    if not text:
        raise ValueError("empty amount")
    text = re.sub(r"^R\$\s*", "", text, flags=re.IGNORECASE).strip()
    normalized = text.replace(".", "").replace(",", ".")
    return float(normalized)


def ibge7_from_municipality_ibge6(code: str) -> str:
    """Derive IBGE7 check digit from the official 6-digit municipality stem."""
    digits = str(code or "").strip()
    if not re.fullmatch(r"\d{6}", digits):
        return ""
    weights = (1, 2, 1, 2, 1, 2)
    total = 0
    for digit, weight in zip(digits, weights, strict=True):
        product = int(digit) * weight
        total += product // 10 + product % 10
    check = (10 - (total % 10)) % 10
    return f"{digits}{check}"


_RO_MONTH_ABBR = {
    "JAN": "01",
    "FEV": "02",
    "MAR": "03",
    "ABR": "04",
    "MAI": "05",
    "JUN": "06",
    "JUL": "07",
    "AGO": "08",
    "SET": "09",
    "OUT": "10",
    "NOV": "11",
    "DEZ": "12",
}


def _ro_month_competence(header: str, *, competence_year: str) -> str | None:
    """Map RO wide headers (01/2022 or jan/22) to YYYY-MM when year matches."""
    year_filter = str(competence_year or "").strip()[:4]
    label = str(header or "").strip()
    slash = re.fullmatch(r"(\d{2})/(\d{4})", label)
    if slash:
        month, year = slash.group(1), slash.group(2)
        if year_filter and year != year_filter:
            return None
        if 1 <= int(month) <= 12:
            return f"{year}-{month}"
        return None
    abbr = re.fullmatch(r"([A-Za-z]{3})/(\d{2})", label)
    if abbr:
        month = _RO_MONTH_ABBR.get(abbr.group(1).upper())
        year = f"20{abbr.group(2)}"
        if not month:
            return None
        if year_filter and year != year_filter:
            return None
        return f"{year}-{month}"
    return None


def parse_state_ro_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "RO",
    competence_year: str = "2022",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse RO SEFIN wide CSV (ICMS name-only or IPVA IBGE6); no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state RO tax filter: {tax}")
    year = str(competence_year or "2022").strip()[:4]
    reader = csv.DictReader(io.StringIO(_decode_csv_bytes(body)), delimiter=";")
    fieldnames = list(reader.fieldnames or [])
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    month_fields = [
        (name, competence)
        for name in fieldnames
        if (competence := _ro_month_competence(name, competence_year=year))
    ]
    if not month_fields:
        return [], [({"rowId": "ro-header"}, f"missing monthly columns for {year}")]

    def _name_key(item: dict) -> str:
        for key in item:
            if "MUNICIP" in normalize_place(key):
                return str(item.get(key) or "").strip()
        return ""

    def _code_key(item: dict) -> str:
        for key in item:
            if normalize_place(key) in {"CODIGO", "CODIGO IBGE", "COD"}:
                return str(item.get(key) or "").strip()
        return str(item.get("Código") or item.get("Codigo") or "").strip()

    for index, item in enumerate(reader):
        raw_name = _name_key(item)
        place = normalize_place(raw_name)
        if not place or place.startswith("TOTAL") or place.startswith("TOTAL LIQUIDO"):
            continue
        code6 = _code_key(item)
        ibge = ibge7_from_municipality_ibge6(code6)
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            ibge = lookup.get((place, normalize_place(uf)), "")
        for field_name, competence in month_fields:
            amount_raw = item.get(field_name)
            try:
                value = parse_brazilian_number(amount_raw)
            except (TypeError, ValueError):
                quarantined.append(
                    (
                        {
                            "rowId": f"ro-{tax_key.lower()}-{index}-{competence}",
                            "territoryName": raw_name,
                            "uf": uf,
                            "value": amount_raw,
                        },
                        f"non numeric {tax_key} amount",
                    )
                )
                continue
            row = {
                "rowId": f"ro-{tax_key.lower()}-{ibge or index}-{competence}"[:64],
                "territoryName": raw_name,
                "uf": uf,
                "ibgeCode": ibge,
                "competence": competence,
                "transferName": tax_key,
                "modality": modality,
                "value": value,
                "unit": "BRL",
            }
            if not IBGE_MUNICIPALITY.fullmatch(ibge):
                quarantined.append((row, "missing IBGE municipality code"))
                continue
            silver.append(row)
    return silver, quarantined


def parse_state_ce_xls(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "CE",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_ce_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI"}:
        raise ValueError(f"unsupported state CE tax filter: {tax}")
    competence_key = str(competence or "2025-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid CE competence: {competence}")
    try:
        book = xlrd.open_workbook(file_contents=body)
    except (XLRDError, OSError, ValueError) as exc:
        return [], [({"rowId": "ce-header"}, f"invalid XLS: {exc}")]
    sheet = book.sheet_by_index(0)
    header_row = None
    for row_index in range(min(sheet.nrows, 20)):
        first = normalize_place(str(sheet.cell_value(row_index, 0) or ""))
        if first.startswith("MUNICIP"):
            header_row = row_index
            break
    if header_row is None:
        return [], [({"rowId": "ce-header"}, "missing Município header")]
    # Official layout: Município | ICMS Total/... | IPVA Total/... | IPI Total/...
    amount_col = {"ICMS": 1, "IPVA": 4, "IPI": 7}[tax_key]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index in range(header_row + 2, sheet.nrows):
        raw_name = str(sheet.cell_value(index, 0) or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        amount_raw = sheet.cell_value(index, amount_col) if amount_col < sheet.ncols else None
        try:
            if isinstance(amount_raw, (int, float)) and not isinstance(amount_raw, bool):
                value = float(amount_raw)
            else:
                value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"ce-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"ce-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


_RS_MONTH_NAMES = {
    "01": "JANEIRO",
    "02": "FEVEREIRO",
    "03": "MARCO",
    "04": "ABRIL",
    "05": "MAIO",
    "06": "JUNHO",
    "07": "JULHO",
    "08": "AGOSTO",
    "09": "SETEMBRO",
    "10": "OUTUBRO",
    "11": "NOVEMBRO",
    "12": "DEZEMBRO",
}

_RN_MONTH_NAMES = {
    "01": "JANEIRO",
    "02": "FEVEREIRO",
    "03": "MARCO",
    "04": "ABRIL",
    "05": "MAIO",
    "06": "JUNHO",
    "07": "JULHO",
    "08": "AGOSTO",
    "09": "SETEMBRO",
    "10": "OUTUBRO",
    "11": "NOVEMBRO",
    "12": "DEZEMBRO",
}

_MA_MONTH_NAMES = _RN_MONTH_NAMES


def parse_state_ma_xls(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "MA",
    competence: str = "2026-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFAZ-MA Repasses Municipais XLS; semester sheets; name+UF join.

    IPI is published as FPEX (Fundo de Participação nas Exportações / IPI-Exportação).
    """
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_ma_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI"}:
        raise ValueError(f"unsupported state MA tax filter: {tax}")
    sheet_tax = "FPEX" if tax_key == "IPI" else tax_key
    competence_key = str(competence or "2026-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid MA competence: {competence}")
    _year, month = competence_key.split("-")
    month_name = _MA_MONTH_NAMES[month]
    semester_token = "1" if month <= "06" else "2"
    try:
        book = xlrd.open_workbook(file_contents=body)
    except (XLRDError, OSError, ValueError) as exc:
        return [], [({"rowId": "ma-header"}, f"invalid XLS: {exc}")]
    sheet = None
    for index in range(book.nsheets):
        candidate = book.sheet_by_index(index)
        label = normalize_place(candidate.name)
        if sheet_tax in label and semester_token in label and "SEMESTRE" in label:
            sheet = candidate
            break
    if sheet is None:
        return [], [
            (
                {"rowId": "ma-header"},
                f"missing sheet {sheet_tax} {semester_token}o Semestre",
            )
        ]
    if sheet.nrows < 12 or sheet.ncols < 2:
        return [], [({"rowId": "ma-header"}, "empty workbook")]
    header_row = None
    for row_index in range(min(sheet.nrows, 16)):
        first = normalize_place(str(sheet.cell_value(row_index, 0) or ""))
        if first.startswith("MUNICIP"):
            header_row = row_index
            break
    if header_row is None:
        return [], [({"rowId": "ma-header"}, "missing MUNICIPIOS header")]
    month_header_row = header_row + 1 if header_row + 1 < sheet.nrows else header_row
    amount_col = None
    for col in range(sheet.ncols):
        label = normalize_place(str(sheet.cell_value(month_header_row, col) or ""))
        if label == month_name or label.startswith(month_name):
            amount_col = col
            break
    if amount_col is None:
        return [], [({"rowId": "ma-header"}, f"missing month column {month_name}")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index in range(month_header_row + 1, sheet.nrows):
        raw_name = str(sheet.cell_value(index, 0) or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        amount_raw = sheet.cell_value(index, amount_col) if amount_col < sheet.ncols else None
        try:
            if isinstance(amount_raw, (int, float)) and not isinstance(amount_raw, bool):
                value = float(amount_raw)
            else:
                value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"ma-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"ma-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": round(value, 2),
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_rn_xls(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "RN",
    competence: str = "2026-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFAZ-RN Repasses Prefeituras XLS; sheets ICMS/IPVA/IPI; monthly column."""
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_rn_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI"}:
        raise ValueError(f"unsupported state RN tax filter: {tax}")
    competence_key = str(competence or "2026-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid RN competence: {competence}")
    _year, month = competence_key.split("-")
    month_name = _RN_MONTH_NAMES[month]
    try:
        book = xlrd.open_workbook(file_contents=body)
    except (XLRDError, OSError, ValueError) as exc:
        return [], [({"rowId": "rn-header"}, f"invalid XLS: {exc}")]
    try:
        sheet = book.sheet_by_name(tax_key)
    except xlrd.XLRDError:
        return [], [({"rowId": "rn-header"}, f"missing sheet {tax_key}")]
    if sheet.nrows < 11 or sheet.ncols < 2:
        return [], [({"rowId": "rn-header"}, "empty workbook")]
    header_row = None
    for row_index in range(min(sheet.nrows, 12)):
        first = normalize_place(str(sheet.cell_value(row_index, 0) or ""))
        if first.startswith("MUNICIP"):
            header_row = row_index
            break
    if header_row is None:
        return [], [({"rowId": "rn-header"}, "missing MUNICIPIOS header")]
    amount_col = None
    for col in range(sheet.ncols):
        label = normalize_place(str(sheet.cell_value(header_row, col) or ""))
        if label == month_name or label.startswith(month_name):
            amount_col = col
            break
    if amount_col is None:
        return [], [({"rowId": "rn-header"}, f"missing month column {month_name}")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index in range(header_row + 1, sheet.nrows):
        raw_name = str(sheet.cell_value(index, 0) or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        amount_raw = sheet.cell_value(index, amount_col) if amount_col < sheet.ncols else None
        try:
            if isinstance(amount_raw, (int, float)) and not isinstance(amount_raw, bool):
                value = float(amount_raw)
            else:
                value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"rn-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"rn-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": round(value, 2),
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_rs_xls(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "RS",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFAZ-RS MontaArquivo XLS; ICMS/IPVA mensais ou Compensação LC194."""
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_rs_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "COMPENSACAO_LC194"}:
        raise ValueError(f"unsupported state RS tax filter: {tax}")
    competence_key = str(competence or "2025-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid RS competence: {competence}")
    year, month = competence_key.split("-")
    month_name = _RS_MONTH_NAMES[month]
    try:
        book = xlrd.open_workbook(file_contents=body)
    except (XLRDError, OSError, ValueError) as exc:
        return [], [({"rowId": "rs-header"}, f"invalid XLS: {exc}")]
    sheet = None
    if tax_key == "COMPENSACAO_LC194":
        for index in range(book.nsheets):
            candidate = book.sheet_by_index(index)
            label = normalize_place(candidate.name)
            if candidate.nrows > 0 and month_name in label and year in label:
                sheet = candidate
                break
        if sheet is None:
            return [], [
                (
                    {"rowId": "rs-header"},
                    f"missing sheet {month_name} {year} for Compensação LC194",
                )
            ]
    else:
        for index in range(book.nsheets):
            candidate = book.sheet_by_index(index)
            if candidate.nrows > 0 and candidate.ncols > 0:
                sheet = candidate
                break
    if sheet is None:
        return [], [({"rowId": "rs-header"}, "empty workbook")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"

    if tax_key == "COMPENSACAO_LC194":
        header_row = None
        for row_index in range(min(sheet.nrows, 10)):
            first = normalize_place(str(sheet.cell_value(row_index, 0) or ""))
            if first.startswith("MUNICIP"):
                header_row = row_index
                break
        if header_row is None:
            return [], [({"rowId": "rs-header"}, "missing MUNICIPIO header")]
        amount_col = None
        for probe_row in range(header_row, min(header_row + 3, sheet.nrows)):
            for col in range(sheet.ncols):
                label = normalize_place(str(sheet.cell_value(probe_row, col) or ""))
                if "REPASSE" in label:
                    amount_col = col
                    break
            if amount_col is not None:
                break
        if amount_col is None:
            return [], [({"rowId": "rs-header"}, "missing REPASSE column")]
        data_start = header_row + 2
    elif tax_key == "ICMS":
        header_row = None
        for row_index in range(min(sheet.nrows, 10)):
            first = normalize_place(str(sheet.cell_value(row_index, 0) or ""))
            if first.startswith("MUNICIP"):
                header_row = row_index
                break
        if header_row is None:
            return [], [({"rowId": "rs-header"}, "missing MUNICIPIO header")]
        amount_col = None
        for col in range(sheet.ncols):
            label = normalize_place(str(sheet.cell_value(header_row, col) or ""))
            if label.startswith("TOTAL") and month_name in label and year in label:
                amount_col = col
                break
        if amount_col is None:
            return [], [
                (
                    {"rowId": "rs-header"},
                    f"missing TOTAL {month_name}/{year} REPASSE column",
                )
            ]
        data_start = header_row + 2
    else:
        header_row = 0
        amount_col = None
        for col in range(sheet.ncols):
            label = normalize_place(str(sheet.cell_value(header_row, col) or ""))
            if label in {"TOTAL MES", "TOTAL DO MES"} or label.startswith("TOTAL MES"):
                amount_col = col
                break
        if amount_col is None:
            return [], [({"rowId": "rs-header"}, "missing Total Mês column")]
        data_start = header_row + 1

    for index in range(data_start, sheet.nrows):
        raw_name = str(sheet.cell_value(index, 0) or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if (
            place in {"TOTAL", "TOTAIS"}
            or place.startswith("TOTAL")
            or place.startswith("REPASSE TOTAL")
            or place.startswith("SAC ")
            or place.startswith("OUVIDORIA")
            or place.startswith("*")
            or set(place) <= {"-", " "}
            or "DEBITO" in place
        ):
            continue
        amount_raw = sheet.cell_value(index, amount_col) if amount_col < sheet.ncols else None
        try:
            if isinstance(amount_raw, (int, float)) and not isinstance(amount_raw, bool):
                value = float(amount_raw)
            else:
                value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"rs-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"rs-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def _ibge7_from_xls_cell(raw: object) -> str:
    if isinstance(raw, bool):
        return ""
    if isinstance(raw, (int, float)):
        if float(raw).is_integer():
            return str(int(raw))
        return ""
    text = str(raw or "").strip()
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".", maxsplit=1)[0]
    digits = re.sub(r"\D", "", text)
    return digits if len(digits) == 7 else text


def parse_state_al_xls(
    body: bytes,
    *,
    tax: str,
    uf: str = "AL",
    competence_year: str = "2021",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse AL dados.al.gov.br annual XLS; native IBGE7; ICMS/IPVA/IPI/ROYALTY; no credit."""
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_al_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI", "ROYALTY"}:
        raise ValueError(f"unsupported state AL tax filter: {tax}")
    year = str(competence_year or "2021").strip()[:4]
    if not re.fullmatch(r"\d{4}", year):
        raise ValueError(f"invalid AL competence_year: {competence_year}")
    try:
        book = xlrd.open_workbook(file_contents=body)
    except (XLRDError, OSError, ValueError) as exc:
        return [], [({"rowId": "al-header"}, f"invalid XLS: {exc}")]
    sheet = book.sheet_by_index(0)
    if sheet.nrows < 2 or sheet.ncols < 3:
        return [], [({"rowId": "al-header"}, "empty workbook")]
    headers = [str(sheet.cell_value(0, col) or "").strip() for col in range(sheet.ncols)]
    amount_col = None
    for index, name in enumerate(headers):
        place = normalize_place(name)
        column_token = "ROYALT" if tax_key == "ROYALTY" else tax_key
        if column_token not in place or year not in place:
            continue
        if tax_key == "ICMS" and ("IPVA" in place or "IPI" in place or "ROYALT" in place):
            continue
        if tax_key == "IPVA" and ("IPI" in place or "ROYALT" in place):
            continue
        if tax_key == "IPI" and ("IPVA" in place or "ICMS" in place or "ROYALT" in place):
            continue
        if tax_key == "ROYALTY" and ("IPI" in place or "IPVA" in place or "ICMS" in place):
            continue
        amount_col = index
        break
    if amount_col is None:
        return [], [({"rowId": "al-header"}, f"missing {tax_key} Total {year} column")]
    ibge_col = next(
        (index for index, name in enumerate(headers) if "CODIGO" in normalize_place(name)),
        0,
    )
    name_col = next(
        (index for index, name in enumerate(headers) if "MUNICIP" in normalize_place(name)),
        1 if sheet.ncols > 1 else 0,
    )
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index in range(1, sheet.nrows):
        raw_name = str(sheet.cell_value(index, name_col) or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS", "ALAGOAS"} or place.startswith("TOTAL"):
            continue
        ibge = _ibge7_from_xls_cell(sheet.cell_value(index, ibge_col))
        amount_raw = sheet.cell_value(index, amount_col)
        try:
            if isinstance(amount_raw, (int, float)) and not isinstance(amount_raw, bool):
                value = float(amount_raw)
            else:
                value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"al-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        row = {
            "rowId": f"al-{tax_key.lower()}-{ibge or index}-{year}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": year,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_ac_csv(
    body: bytes,
    *,
    tax: str,
    uf: str = "AC",
    competence_year: str = "2021",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse AC SEPLAG wide annual CSV; native IBGE7; ICMS only; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key != "ICMS":
        raise ValueError(f"unsupported state AC tax filter: {tax}")
    year = str(competence_year or "2021").strip()[:4]
    reader = csv.reader(io.StringIO(_decode_csv_bytes(body)), delimiter=";")
    rows = list(reader)
    if not rows:
        return [], [({"rowId": "ac-header"}, "empty CSV")]
    header = [str(cell or "").strip() for cell in rows[0]]
    year_indexes = {
        str(name).strip(): index
        for index, name in enumerate(header)
        if re.fullmatch(r"\d{4}", str(name or "").strip())
    }
    if year not in year_indexes:
        return [], [({"rowId": "ac-header"}, f"missing year column {year}")]
    amount_index = year_indexes[year]
    ibge_index = next(
        (index for index, name in enumerate(header) if "IBGE" in normalize_place(name)),
        1 if len(header) > 1 else None,
    )
    if ibge_index is None:
        return [], [({"rowId": "ac-header"}, "missing Cod IBGE column")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(rows[1:]):
        if not item:
            continue
        raw_name = str(item[0] or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"ACRE", "TOTAL"} or place.startswith("TOTAL"):
            continue
        ibge = str(item[ibge_index] if len(item) > ibge_index else "").strip()
        if len(item) <= amount_index:
            quarantined.append(
                (
                    {
                        "rowId": f"ac-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                    },
                    f"missing {tax_key} column",
                )
            )
            continue
        amount_raw = item[amount_index]
        try:
            value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"ac-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        row = {
            "rowId": f"ac-{tax_key.lower()}-{ibge or index}-{year}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": year,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_pi_repasseweb_html(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "PI",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFAZ-PI Repasse WEB HTML table; aggregate bank rows; join IBGE7 by name+UF."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state PI Repasse WEB tax filter: {tax}")
    competence_key = str(competence or "2025-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid PI Repasse WEB competence: {competence}")
    year, month = competence_key.split("-")
    period_key = f"{year}{month}"
    try:
        html = body.decode("utf-8")
    except UnicodeDecodeError:
        html = body.decode("latin-1")
    lookup = ibge_lookup or {}
    aggregated: dict[str, dict[str, object]] = {}
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for match in re.finditer(r"<tr[^>]*data-ri=\"[^\"]*\"[^>]*>([\s\S]*?)</tr>", html, re.I):
        cells = [
            re.sub(r"<[^>]+>", "", cell).strip()
            for cell in re.findall(r"<td[^>]*>([\s\S]*?)</td>", match.group(1), re.I)
        ]
        if len(cells) < 7:
            continue
        period = cells[0].strip()
        if period != period_key:
            continue
        raw_name = cells[1].strip()
        if raw_name.upper().endswith(f"-{uf}"):
            raw_name = raw_name[: -(len(uf) + 1)].strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        try:
            value = parse_brazilian_number(cells[6])
        except ValueError:
            quarantined.append(
                (
                    {
                        "rowId": f"pi-rw-{tax_key.lower()}-{place or 'unknown'}-{competence_key}"[
                            :64
                        ],
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": cells[6],
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        bucket = aggregated.get(place)
        if bucket is None:
            aggregated[place] = {
                "territoryName": raw_name,
                "value": value,
            }
        else:
            bucket["value"] = round(float(bucket["value"]) + value, 2)
    silver: list[dict] = []
    for place, payload in sorted(aggregated.items()):
        raw_name = str(payload["territoryName"])
        value = float(payload["value"])
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"pi-rw-{tax_key.lower()}-{ibge or place}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_pr_html(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "PR",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFA/PR monthly HTML transfer report; ICMS líquido, FPEX/IPI, royalties, IPVA.

    Join IBGE7 by name+UF. IPI is published as Fundo de Exportação (FPEX).
    """
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI", "ROYALTY"}:
        raise ValueError(f"unsupported state PR HTML tax filter: {tax}")
    competence_key = str(competence or "2025-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid PR HTML competence: {competence}")
    try:
        html = body.decode("utf-8")
    except UnicodeDecodeError:
        html = body.decode("latin-1")
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    # Columns: município, FPM, ICMS bruto, ICMS líquido, FPEX, royalties, IPVA, total.
    amount_index = {"ICMS": 3, "IPI": 4, "ROYALTY": 5, "IPVA": 6}[tax_key]
    for match in re.finditer(r"<tr[^>]*>([\s\S]*?)</tr>", html, re.I):
        cells = [
            re.sub(r"<[^>]+>", "", cell).strip()
            for cell in re.findall(r"<td[^>]*>([\s\S]*?)</td>", match.group(1), re.I)
        ]
        if len(cells) < 7:
            continue
        raw_name = cells[0].strip()
        place = normalize_place(raw_name)
        if not place or place in {"MUNICIPIO", "TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        if place.startswith("INDICE") or place.startswith("ICMS"):
            continue
        raw_amount = cells[amount_index] if len(cells) > amount_index else ""
        try:
            value = parse_brazilian_number(raw_amount)
        except ValueError:
            quarantined.append(
                (
                    {
                        "rowId": f"pr-html-{tax_key.lower()}-{place or 'unknown'}-{competence_key}"[
                            :64
                        ],
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": raw_amount,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"pr-html-{tax_key.lower()}-{ibge or place}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


_PA_VERDE_MONTHS = {
    "01": "JANEIRO",
    "02": "FEVEREIRO",
    "03": "MARCO",
    "04": "ABRIL",
    "05": "MAIO",
    "06": "JUNHO",
    "07": "JULHO",
    "08": "AGOSTO",
    "09": "SETEMBRO",
    "10": "OUTUBRO",
    "11": "NOVEMBRO",
    "12": "DEZEMBRO",
}


def _iter_xlsx_matrix(body: bytes, *, sheet_name: str | None = None) -> list[list[str]]:
    """Read a worksheet as a matrix without treating row 0 as a dict header.

    When sheet_name is set, select that workbook tab (e.g. GO Economia ``11-2024``).
    Otherwise use the first worksheet / ``sheet1.xml``.
    """
    import zipfile
    from xml.etree import ElementTree as ET

    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", ns):
                texts = [
                    node.text or ""
                    for node in item.iter(
                        "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                    )
                ]
                shared.append("".join(texts))
        sheet_path = "xl/worksheets/sheet1.xml"
        if sheet_name:
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            rid_to_target = {
                rel.get("Id"): rel.get("Target")
                for rel in rels
                if rel.get("Id") and rel.get("Target")
            }
            resolved = None
            for sheet in workbook.findall("m:sheets/m:sheet", ns):
                if sheet.get("name") != sheet_name:
                    continue
                rid = sheet.get(f"{rel_ns}id")
                target = rid_to_target.get(rid or "")
                if target:
                    resolved = "xl/" + str(target).lstrip("/")
                break
            if not resolved or resolved not in archive.namelist():
                raise ValueError(f"missing XLSX sheet: {sheet_name}")
            sheet_path = resolved
        elif sheet_path not in archive.namelist():
            return []
        xml = archive.read(sheet_path)
    rows: list[list[str]] = []
    for row_xml in re.findall(rb"<row[^>]*>.*?</row>", xml, flags=re.S):
        cells: dict[int, str] = {}
        for match in re.finditer(
            rb'<c r="([A-Z]+)(\d+)"([^>]*)>(?:<v>(.*?)</v>)?',
            row_xml,
        ):
            col = match.group(1).decode("ascii")
            attrs = match.group(3).decode("ascii")
            raw = match.group(4).decode("utf-8") if match.group(4) is not None else ""
            if 't="s"' in attrs and raw.isdigit():
                value = shared[int(raw)] if int(raw) < len(shared) else raw
            else:
                value = raw
            index = 0
            for char in col:
                index = index * 26 + (ord(char) - 64)
            cells[index - 1] = value
        if not cells:
            continue
        width = max(cells) + 1
        rows.append([cells.get(i, "") for i in range(width)])
    return rows


def _compact_header(value: str) -> str:
    return normalize_place(value).replace(" ", "")


def _go_economia_tax_column(compacted: list[str], tax_key: str) -> int | None:
    """Locate tax group column; IPI may appear as IPI-EXPORTACAO."""
    if tax_key in compacted:
        return compacted.index(tax_key)
    for index, label in enumerate(compacted):
        if label.startswith(tax_key):
            return index
    return None


def parse_state_go_economia_xlsx(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "GO",
    competence: str = "2024-11",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse Secretaria da Economia/GO monthly XLSX (ICMS/IPVA/IPI Bruto); join IBGE7 by name+UF.

    Sheet tabs are ``MM-YYYY``. Amount is the tax-group ``Bruto`` column (constitutional
    quota before FUNDEB retention). IPI is published as IPI-Exportação. Does not create
    tax credit.
    """
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI"}:
        raise ValueError(f"unsupported state GO Economia tax filter: {tax}")
    competence_key = str(competence or "2024-11").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid GO Economia competence: {competence}")
    year, month = competence_key.split("-")
    sheet_label = f"{month}-{year}"
    try:
        matrix = _iter_xlsx_matrix(body, sheet_name=sheet_label)
    except ValueError as exc:
        return [], [({"rowId": "go-economia-document"}, str(exc))]
    except Exception as exc:  # noqa: BLE001 — invalid OOXML surfaces as quarantine
        return [], [({"rowId": "go-economia-document"}, f"invalid XLSX: {exc}")]
    if len(matrix) < 3:
        return [], [({"rowId": "go-economia-document"}, "missing Economia rows")]
    group_row_index = None
    tax_col = None
    name_col = None
    for index, row in enumerate(matrix[:20]):
        compacted = [_compact_header(cell) for cell in row]
        if "MUNICIPIOS" not in compacted:
            continue
        found = _go_economia_tax_column(compacted, tax_key)
        if found is None:
            continue
        group_row_index = index
        name_col = compacted.index("MUNICIPIOS")
        tax_col = found
        break
    if group_row_index is None or tax_col is None or name_col is None:
        return [], [({"rowId": "go-economia-header"}, f"missing {tax_key}/MUNICIPIOS header")]
    if group_row_index + 1 >= len(matrix):
        return [], [({"rowId": "go-economia-header"}, "missing Bruto subheader row")]
    sub = [_compact_header(cell) for cell in matrix[group_row_index + 1]]
    amount_col = tax_col
    if amount_col >= len(sub) or sub[amount_col] != "BRUTO":
        for col, label in enumerate(sub):
            if label == "BRUTO" and col >= tax_col:
                amount_col = col
                break
        else:
            return [], [({"rowId": "go-economia-header"}, f"missing {tax_key} Bruto column")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, row in enumerate(matrix[group_row_index + 2 :], start=group_row_index + 2):
        if name_col >= len(row):
            continue
        raw_name = str(row[name_col] or "").strip()
        place = normalize_place(raw_name)
        if not place or place in {"MUNICIPIOS", "TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        raw_amount = row[amount_col] if amount_col < len(row) else ""
        try:
            value = float(str(raw_amount).strip().replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"go-eco-{tax_key.lower()}-{place or index}-{competence_key}"[:64],
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": raw_amount,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        out = {
            "rowId": f"go-eco-{tax_key.lower()}-{ibge or place}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((out, "missing IBGE municipality code"))
            continue
        silver.append(out)
    return silver, quarantined


def parse_state_pa_icms_verde_xlsx(
    body: bytes,
    *,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "PA",
    competence: str = "2024-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEMAS/PA ICMS Verde monthly XLSX (ecological 8% slice); join IBGE7 by name+UF.

    Publishes modality ICMS_VERDE_QUOTA — not full constitutional ICMS quota.
    """
    competence_key = str(competence or "2024-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid PA ICMS Verde competence: {competence}")
    month_key = competence_key[5:7]
    month_label = _PA_VERDE_MONTHS.get(month_key)
    if not month_label:
        raise ValueError(f"unsupported PA ICMS Verde month: {competence}")
    try:
        matrix = _iter_xlsx_matrix(body)
    except Exception as exc:  # noqa: BLE001 — invalid OOXML surfaces as quarantine
        return [], [({"rowId": "pa-icms-verde-document"}, f"invalid XLSX: {exc}")]
    if len(matrix) < 3:
        return [], [({"rowId": "pa-icms-verde-document"}, "missing ICMS Verde rows")]
    month_row_index = None
    amount_col = None
    for index, row in enumerate(matrix[:5]):
        normalized = [normalize_place(cell) for cell in row]
        if month_label in normalized:
            for col, label in enumerate(normalized):
                if label == month_label:
                    month_row_index = index
                    amount_col = col
                    break
        if amount_col is not None:
            break
    if month_row_index is None or amount_col is None:
        return [], [({"rowId": "pa-icms-verde-header"}, f"missing month column {month_label}")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, row in enumerate(matrix[month_row_index + 1 :], start=month_row_index + 1):
        if not row:
            continue
        raw_name = str(row[0] or "").strip()
        place = normalize_place(raw_name)
        if not place or place in {"MUNICIPIOS", "TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        if place.startswith("MESES"):
            continue
        raw_amount = row[amount_col] if amount_col < len(row) else ""
        try:
            value = float(str(raw_amount).strip().replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"pa-icms-verde-{place or index}-{competence_key}"[:64],
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": raw_amount,
                    },
                    "non numeric ICMS_VERDE amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        out = {
            "rowId": f"pa-icms-verde-{ibge or place}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": "ICMS_VERDE",
            "modality": "ICMS_VERDE_QUOTA",
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((out, "missing IBGE municipality code"))
            continue
        silver.append(out)
    return silver, quarantined


def parse_state_ac_transparencia_json(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "AC",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse AC Transparência JSON export (ICMS/IPVA/FUNDEB); join IBGE7 by name+UF; no credit."""
    tax_key = str(tax or "").strip().upper()
    amount_fields = {
        "ICMS": "valor_icms",
        "IPVA": "valor_ipva",
        "FUNDEB": "valor_fundeb",
    }
    if tax_key not in amount_fields:
        raise ValueError(f"unsupported state AC Transparência tax filter: {tax}")
    competence_key = str(competence or "2025-01").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError(f"invalid AC Transparência competence: {competence}")
    year, month = competence_key.split("-")
    amount_field = amount_fields[tax_key]
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "ac-transparencia-document"}, "invalid JSON")]
    if not isinstance(payload, list):
        return [], [({"rowId": "ac-transparencia-document"}, "unexpected envelope")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            continue
        row_year = str(item.get("ano") or "").strip()
        row_month = str(item.get("mes") or "").strip().zfill(2)
        if row_year and row_year != year:
            continue
        if row_month and row_month != month:
            continue
        raw_name = str(item.get("municipio") or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        if place in {"TOTAL", "TOTAIS"} or place.startswith("TOTAL"):
            continue
        amount_raw = item.get(amount_field)
        try:
            value = float(str(amount_raw).replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"ac-tr-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((place, normalize_place(uf)), "")
        row = {
            "rowId": f"ac-tr-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def _decode_csv_bytes(body: bytes) -> str:
    payload = body
    if len(payload) >= 2 and payload[0] == 0x1F and payload[1] == 0x8B:
        payload = gzip.decompress(payload)
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        return payload.decode("latin-1")


def parse_state_mg_csv(
    body: bytes,
    *,
    tax: str,
    municipio_dim: bytes | None = None,
    tempo_dim: bytes | None = None,
    uf: str = "MG",
    competence_year: str = "2024",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse MG frictionless fact CSV.gz with municipio/tempo dims; native IBGE7."""
    tax_key = str(tax or "").strip().upper()
    amount_fields = {"ICMS": "vr_icms", "IPVA": "vr_ipva", "IPI": "vr_ipi"}
    if tax_key not in amount_fields:
        raise ValueError(f"unsupported state MG tax filter: {tax}")
    amount_field = amount_fields[tax_key]
    year = str(competence_year or "2024").strip()[:4]
    municipio_by_id: dict[str, dict[str, str]] = {}
    if municipio_dim:
        mun_reader = csv.DictReader(io.StringIO(_decode_csv_bytes(municipio_dim)), delimiter=";")
        for item in mun_reader:
            municipio_by_id[str(item.get("id_municipio") or "").strip()] = {
                "ibge": str(item.get("cd_municipio_ibge") or "").strip(),
                "nome": str(item.get("nome") or "").strip(),
            }
    tempo_by_id: dict[str, dict[str, str]] = {}
    if tempo_dim:
        tempo_reader = csv.DictReader(io.StringIO(_decode_csv_bytes(tempo_dim)), delimiter=";")
        for item in tempo_reader:
            tempo_by_id[str(item.get("id_tempo") or "").strip()] = {
                "ano": str(item.get("ano") or "").strip(),
                "mes": str(item.get("mes") or "").strip().zfill(2),
                "anomes_iso": str(item.get("anomes_iso") or "").strip(),
            }
    fact_reader = csv.DictReader(io.StringIO(_decode_csv_bytes(body)), delimiter=";")
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(fact_reader):
        mun_id = str(item.get("id_municipio") or "").strip()
        tempo_id = str(item.get("id_tempo") or "").strip()
        part_year = str(item.get("ano_particao") or "").strip()
        tempo = tempo_by_id.get(tempo_id, {})
        if tempo.get("ano"):
            if tempo["ano"] != year:
                continue
            month = tempo.get("mes") or "00"
            if not month.isdigit() or not (1 <= int(month) <= 12):
                continue
            competence = f"{tempo['ano']}-{month}"
        elif part_year == year:
            competence = year
        else:
            continue
        mun = municipio_by_id.get(mun_id, {})
        ibge = mun.get("ibge") or ""
        raw_name = mun.get("nome") or ""
        amount_raw = item.get(amount_field)
        try:
            value = float(str(amount_raw).strip().replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"mg-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        row = {
            "rowId": f"mg-{tax_key.lower()}-{ibge or mun_id}-{competence}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_es_csv(
    body: bytes,
    *,
    tax: str,
    uf: str = "ES",
    competence_year: str = "2024",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse ES TransfEstadoMunicipios CSV; native IBGE7 in CodMunicipio; no credit."""
    tax_key = str(tax or "").strip().upper()
    amount_fields = {
        "ICMS": "IcmsTotal",
        "IPVA": "Ipva",
        "IPI": "Ipi",
        "CIDE": "CotaParteCide",
        "FRD": "FundoReducaoDesigualdades",
        "COMPENSACAO": "CompensacaoFinanceira",
    }
    if tax_key not in amount_fields:
        raise ValueError(f"unsupported state ES tax filter: {tax}")
    amount_field = amount_fields[tax_key]
    year = str(competence_year or "2024").strip()[:4]
    reader = csv.DictReader(io.StringIO(_decode_csv_bytes(body)), delimiter=";")
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(reader):
        row_year = str(item.get("Ano") or "").strip()
        if row_year and row_year != year:
            continue
        month = str(item.get("Mes") or "").strip().zfill(2)
        if not month.isdigit() or not (1 <= int(month) <= 12):
            continue
        competence = f"{year}-{month}"
        ibge = str(item.get("CodMunicipio") or "").strip()
        raw_name = str(item.get("NomeMunicipio") or "").strip()
        amount_raw = item.get(amount_field)
        try:
            value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"es-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        row = {
            "rowId": f"es-{tax_key.lower()}-{ibge or index}-{competence}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_bcb_sgs_olinda(
    body: bytes,
    *,
    series_id: int,
    series_label: str,
    unit: str,
    allowlist: list[int] | tuple[int, ...] | None = None,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse BCB SGS JSON points for one allowlisted series; never tax credit."""
    allowed = {int(item) for item in (allowlist or ())}
    if not allowed:
        raise ValueError("BCB SGS requires a non-empty series_allowlist")
    if int(series_id) not in allowed:
        raise ValueError(f"BCB series {series_id} is outside the configured allowlist")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "bcb-document"}, "invalid JSON")]
    if not isinstance(payload, list):
        return [], [({"rowId": "bcb-document"}, "unexpected SGS envelope")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    label = str(series_label or f"SGS_{series_id}").strip() or f"SGS_{series_id}"
    unit_name = str(unit or "INDEX_POINTS").strip() or "INDEX_POINTS"
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            continue
        raw_date = str(item.get("data") or "").strip()
        raw_value = item.get("valor")
        try:
            value = float(str(raw_value).replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"bcb-sgs-{series_id}-{index}",
                        "territoryName": "Brasil",
                        "uf": "BR",
                        "competence": raw_date or "unknown",
                        "value": raw_value,
                    },
                    "invalid numeric value",
                )
            )
            continue
        if not raw_date:
            quarantined.append(
                (
                    {
                        "rowId": f"bcb-sgs-{series_id}-{index}",
                        "territoryName": "Brasil",
                        "uf": "BR",
                        "value": value,
                    },
                    "missing series date",
                )
            )
            continue
        competence = raw_date.replace("/", "")[:8] or raw_date
        silver.append(
            {
                "rowId": f"bcb-sgs-{series_id}-{competence}"[:64],
                "territoryName": "Brasil",
                "uf": "BR",
                "ibgeCode": "",
                "competence": raw_date,
                "transferName": label,
                "value": value,
                "unit": unit_name,
                "seriesId": str(series_id),
            }
        )
    return silver, quarantined


def parse_bcb_olinda_expectativas(
    body: bytes,
    *,
    indicator_allowlist: list[str] | tuple[str, ...] | None = None,
    max_rows: int = 8,
    value_field: str = "Mediana",
    indicator_units: dict[str, str] | None = None,
    focus_label: str = "FOCUS_ANUAL",
    horizon_field: str = "DataReferencia",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse BCB OLINDA Expectativas OData (anuais/mensais/trimestrais/Selic/inflação); never tax credit."""
    allowed = {
        str(item).strip().upper() for item in (indicator_allowlist or ()) if str(item).strip()
    }
    if not allowed:
        raise ValueError("BCB OLINDA Expectativas requires a non-empty indicator_allowlist")
    units = {
        str(key).strip().upper(): str(value).strip()
        for key, value in (indicator_units or {}).items()
        if str(key).strip() and str(value).strip()
    }
    period = str(focus_label or "FOCUS_ANUAL").strip() or "FOCUS_ANUAL"
    horizon_key = str(horizon_field or "DataReferencia").strip() or "DataReferencia"
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "bcb-olinda-document"}, "invalid JSON")]
    if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
        return [], [({"rowId": "bcb-olinda-document"}, "unexpected OData envelope")]
    field = str(value_field or "Mediana").strip() or "Mediana"
    limit = max(1, int(max_rows or 8))
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(payload["value"]):
        if len(silver) >= limit:
            break
        if not isinstance(item, dict):
            continue
        indicator = str(item.get("Indicador") or "").strip()
        if indicator.upper() not in allowed:
            quarantined.append(
                (
                    {
                        "rowId": f"bcb-olinda-{index}",
                        "territoryName": "Brasil",
                        "uf": "BR",
                        "competence": str(item.get("Data") or "unknown"),
                        "value": item.get(field),
                    },
                    "indicator outside allowlist",
                )
            )
            continue
        raw_date = str(item.get("Data") or "").strip()
        horizon = str(item.get(horizon_key) or item.get("DataReferencia") or "").strip() or "na"
        horizon_token = horizon.replace("/", "-")
        raw_value = item.get(field)
        try:
            value = float(str(raw_value).replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"bcb-olinda-{indicator}-{index}",
                        "territoryName": "Brasil",
                        "uf": "BR",
                        "competence": raw_date or "unknown",
                        "value": raw_value,
                    },
                    "invalid numeric value",
                )
            )
            continue
        if not raw_date:
            quarantined.append(
                (
                    {
                        "rowId": f"bcb-olinda-{indicator}-{index}",
                        "territoryName": "Brasil",
                        "uf": "BR",
                        "value": value,
                    },
                    "missing publication date",
                )
            )
            continue
        detalhe = str(item.get("IndicadorDetalhe") or "").strip()
        label_core = f"{indicator}_{detalhe}" if detalhe else indicator
        label = f"{label_core}_{period}_{horizon_token}"
        if period == "FOCUS_MENSAL":
            default_unit = "PERCENT_PER_MONTH"
        elif period == "FOCUS_TRIMESTRAL":
            default_unit = "BRL_PER_USD" if indicator.upper() == "CÂMBIO" else "PERCENT_PER_QUARTER"
        else:
            default_unit = "BRL_PER_USD" if indicator.upper() == "CÂMBIO" else "PERCENT_PER_YEAR"
        unit = units.get(indicator.upper()) or default_unit
        raw_row_id = f"bcb-olinda-{label_core}-{raw_date}-{horizon_token}"
        if len(raw_row_id) > 64:
            digest = hashlib.sha256(label_core.encode("utf-8")).hexdigest()[:12]
            raw_row_id = f"bcb-olinda-{digest}-{raw_date}-{horizon_token}"
        silver.append(
            {
                "rowId": raw_row_id[:64],
                "territoryName": "Brasil",
                "uf": "BR",
                "ibgeCode": "",
                "competence": raw_date,
                "transferName": label,
                "value": value,
                "unit": unit,
                "seriesId": indicator,
                "horizonYear": horizon,
                "indicatorDetail": detalhe or None,
            }
        )
    return silver, quarantined


def ibge7_from_municipio6(codigo_municipio: str | int) -> str | None:
    """Derive IBGE7 municipality code from CNES/DATASUS 6-digit municipio + check digit."""
    digits = str(codigo_municipio or "").strip()
    if not re.fullmatch(r"\d{6}", digits):
        return None
    weights = (1, 2, 1, 2, 1, 2)
    total = 0
    for index, weight in enumerate(weights):
        product = int(digits[index]) * weight
        total += product if product < 10 else product // 10 + product % 10
    check = (10 - (total % 10)) % 10
    return f"{digits}{check}"


def parse_cnes_datasus_open(
    body: bytes,
    *,
    uf: str,
    codigo_uf: str | int,
    competence: str = "as_published",
    max_rows: int = 8,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse DEMAS CNES estabelecimentos JSON; UF scope; aggregate counts; drop PII."""
    uf_key = normalize_place(uf)
    if not uf_key or len(uf_key) != 2:
        raise ValueError("CNES territorial scope requires a two-letter UF")
    uf_code = str(codigo_uf or "").strip()
    if not re.fullmatch(r"\d{1,2}", uf_code):
        raise ValueError("CNES codigo_uf must be the numeric IBGE UF code")
    uf_code_norm = str(int(uf_code))
    limit = int(max_rows or 0)
    if limit <= 0:
        raise ValueError("CNES max_rows must be a positive integer")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "cnes-document"}, "invalid JSON")]
    if not isinstance(payload, dict) or not isinstance(payload.get("estabelecimentos"), list):
        return [], [({"rowId": "cnes-document"}, "unexpected CNES envelope")]
    counts: dict[str, dict[str, object]] = {}
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(payload.get("estabelecimentos") or []):
        if not isinstance(item, dict):
            continue
        try:
            row_uf_norm = str(int(str(item.get("codigo_uf") or "").strip()))
        except ValueError:
            continue
        if row_uf_norm != uf_code_norm:
            continue
        raw_municipio = item.get("codigo_municipio")
        ibge = ibge7_from_municipio6(raw_municipio)
        if ibge is None:
            quarantined.append(
                (
                    {
                        "rowId": f"cnes-estab-{index}",
                        "territoryName": str(raw_municipio or ""),
                        "uf": uf_key,
                        "ibgeCode": str(raw_municipio or ""),
                        "competence": competence,
                        "value": 1,
                    },
                    "invalid IBGE municipality code",
                )
            )
            continue
        bucket = counts.setdefault(
            ibge,
            {"territoryName": ibge, "uf": uf_key, "count": 0},
        )
        bucket["count"] = int(bucket["count"]) + 1
    silver: list[dict] = []
    for ibge, bucket in sorted(counts.items(), key=lambda item: item[0]):
        if len(silver) >= limit:
            break
        silver.append(
            {
                "rowId": f"cnes-estab-{ibge}-{competence}"[:64],
                "territoryName": str(bucket["territoryName"]),
                "uf": str(bucket["uf"]),
                "ibgeCode": ibge,
                "competence": competence,
                "transferName": "CNES_ESTABELECIMENTOS",
                "value": int(bucket["count"]),
                "unit": "ESTABLISHMENTS",
            }
        )
    return silver, quarantined


def parse_anatel_dados_gov(
    body: bytes,
    *,
    uf: str,
    competence_year: str | int = "2025",
    competence_month: str | int = "11",
    service: str = "Banda Larga Fixa",
    max_rows: int = 8,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse Anatel Meu Município Acessos (ZIP or CSV); UF + IBGE7 scope; no tax credit."""
    uf_key = normalize_place(uf)
    if not uf_key or len(uf_key) != 2:
        raise ValueError("Anatel territorial scope requires a two-letter UF")
    year = str(competence_year or "").strip()
    if not re.fullmatch(r"\d{4}", year):
        raise ValueError("Anatel competence_year must be a four-digit year")
    month = str(competence_month or "").strip().zfill(2)
    if not re.fullmatch(r"\d{2}", month) or not (1 <= int(month) <= 12):
        raise ValueError("Anatel competence_month must be 01..12")
    service_key = str(service or "").strip().casefold()
    if not service_key:
        raise ValueError("Anatel service filter is required")
    limit = int(max_rows or 0)
    if limit <= 0:
        raise ValueError("Anatel max_rows must be a positive integer")
    records = (
        _iter_anatel_zip_acessos_records(body)
        if body[:2] == b"PK"
        else _iter_anatel_csv_records(body)
    )
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, rec in enumerate(records):
        if len(silver) >= limit:
            break
        row_uf = normalize_place(str(_anatel_field(rec, "UF") or ""))
        if row_uf != uf_key:
            continue
        row_year = str(_anatel_field(rec, "Ano") or "").strip()
        row_month = (
            str(_anatel_field(rec, "Mês") or _anatel_field(rec, "Mes") or "").strip().zfill(2)
        )
        if row_year != year or row_month != month:
            continue
        row_service = str(_anatel_field(rec, "Serviço") or _anatel_field(rec, "Servico") or "")
        if row_service.strip().casefold() != service_key:
            continue
        ibge = str(
            _anatel_field(rec, "Código IBGE") or _anatel_field(rec, "Codigo IBGE") or ""
        ).strip()
        raw_name = str(
            _anatel_field(rec, "Município") or _anatel_field(rec, "Municipio") or ""
        ).strip()
        territory = re.sub(rf"\s*-\s*{re.escape(row_uf)}\s*$", "", raw_name, flags=re.I).strip()
        competence = f"{year}-{month}"
        raw_accesses = _anatel_field(rec, "Acessos")
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append(
                (
                    {
                        "rowId": f"anatel-acessos-{index}",
                        "territoryName": territory or raw_name,
                        "uf": row_uf,
                        "ibgeCode": ibge,
                        "competence": competence,
                        "value": raw_accesses,
                    },
                    "invalid IBGE municipality code",
                )
            )
            continue
        try:
            accesses = int(parse_brazilian_number(raw_accesses))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"anatel-acessos-{index}",
                        "territoryName": territory or raw_name or ibge,
                        "uf": row_uf,
                        "ibgeCode": ibge,
                        "competence": competence,
                        "value": raw_accesses,
                    },
                    "invalid access count",
                )
            )
            continue
        silver.append(
            {
                "rowId": f"anatel-scm-{ibge}-{competence}"[:64],
                "territoryName": territory or raw_name or ibge,
                "uf": row_uf,
                "ibgeCode": ibge,
                "competence": competence,
                "transferName": "ANATEL_BANDA_LARGA_FIXA_ACESSOS",
                "value": accesses,
                "unit": "ACCESS_LINES",
            }
        )
    return silver, quarantined


def _anatel_field(rec: dict, key: str) -> object:
    if key in rec:
        return rec.get(key)
    target = key.casefold()
    for actual, value in rec.items():
        if str(actual).casefold() == target:
            return value
    return None


def _iter_anatel_csv_records(body: bytes):
    text = _decode_csv_bytes(body)
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    for row in reader:
        if isinstance(row, dict):
            yield {str(k): (v if v is not None else "") for k, v in row.items()}


def _iter_anatel_zip_acessos_records(body: bytes):
    import zipfile

    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if name.lower().endswith("meu_municipio_acessos.csv")
        ]
        if not candidates:
            return
        yield from _iter_anatel_csv_records(archive.read(candidates[0]))


def parse_epe_open_files(
    body: bytes,
    *,
    uf: str,
    competence_year: str | int = "2024",
    max_rows: int = 8,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse EPE Anuário Dados brutos (CSV fixture or XLSX); UF + year scope; no tax credit."""
    uf_key = normalize_place(uf)
    if not uf_key or len(uf_key) != 2:
        raise ValueError("EPE territorial scope requires a two-letter UF")
    year = str(competence_year or "").strip()
    if not re.fullmatch(r"\d{4}", year):
        raise ValueError("EPE competence_year must be a four-digit year")
    limit = int(max_rows or 0)
    if limit <= 0:
        raise ValueError("EPE max_rows must be a positive integer")
    records = _iter_epe_xlsx_records(body) if body[:2] == b"PK" else _iter_epe_csv_records(body)
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, rec in enumerate(records):
        if len(silver) >= limit:
            break
        row_uf = normalize_place(str(rec.get("UF") or ""))
        if row_uf != uf_key:
            continue
        raw_date = str(rec.get("Data") or "").strip()
        if not raw_date.startswith(year):
            continue
        sector = str(
            rec.get("Setor Econômico - N1") or rec.get("Setor Economico - N1") or ""
        ).strip()
        competence = _epe_competence(raw_date)
        raw_consumers = rec.get("Consumidores")
        try:
            consumers = float(str(raw_consumers).replace(",", "."))
            if consumers != int(consumers):
                raise ValueError("non-integer consumers")
            consumers_i = int(consumers)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"epe-consumers-{index}",
                        "territoryName": row_uf,
                        "uf": row_uf,
                        "competence": competence or raw_date or "unknown",
                        "value": raw_consumers,
                    },
                    "invalid consumer count",
                )
            )
            continue
        if not competence:
            quarantined.append(
                (
                    {
                        "rowId": f"epe-date-{index}",
                        "territoryName": row_uf,
                        "uf": row_uf,
                        "value": consumers_i,
                    },
                    "missing competence date",
                )
            )
            continue
        label = sector or "EPE_CONSUMERS"
        silver.append(
            {
                "rowId": f"epe-{row_uf}-{competence}-{label}"[:64],
                "territoryName": row_uf,
                "uf": row_uf,
                "ibgeCode": "",
                "competence": competence,
                "transferName": label,
                "value": consumers_i,
                "unit": "CONSUMERS",
            }
        )
    return silver, quarantined


def _epe_competence(raw_date: str) -> str:
    digits = re.sub(r"\D", "", raw_date or "")
    if len(digits) >= 6:
        return f"{digits[:4]}-{digits[4:6]}"
    if len(digits) == 4:
        return digits
    return ""


def _iter_epe_csv_records(body: bytes):
    text = _decode_csv_bytes(body)
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if isinstance(row, dict):
            yield {str(k): (v if v is not None else "") for k, v in row.items()}


def _iter_epe_xlsx_records(body: bytes):
    """Minimal XLSX reader (sharedStrings + first sheet) without third-party deps."""
    import zipfile
    from xml.etree import ElementTree as ET

    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", ns):
                texts = [
                    node.text or ""
                    for node in item.iter(
                        "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                    )
                ]
                shared.append("".join(texts))
        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in archive.namelist():
            return
        xml = archive.read(sheet_name)
    header: list[str] | None = None
    for row_xml in re.findall(rb"<row[^>]*>.*?</row>", xml, flags=re.S):
        cells: dict[int, str] = {}
        for match in re.finditer(
            rb'<c r="([A-Z]+)(\d+)"([^>]*)>(?:<v>(.*?)</v>)?',
            row_xml,
        ):
            col = match.group(1).decode("ascii")
            attrs = match.group(3).decode("ascii")
            raw = match.group(4).decode("utf-8") if match.group(4) is not None else ""
            if 't="s"' in attrs and raw.isdigit():
                value = shared[int(raw)] if int(raw) < len(shared) else raw
            else:
                value = raw
            index = 0
            for char in col:
                index = index * 26 + (ord(char) - 64)
            cells[index - 1] = value
        if not cells:
            continue
        width = max(cells) + 1
        values = [cells.get(i, "") for i in range(width)]
        if header is None:
            header = [str(item) for item in values]
            continue
        if len(values) < len(header):
            values = values + [""] * (len(header) - len(values))
        yield dict(zip(header, values, strict=False))


def parse_aneel_ckan_open(
    body: bytes,
    *,
    uf: str,
    competence: str = "as_published",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse ANEEL CKAN datastore IndQual Município; aggregate by IBGE7; UF scope."""
    uf_key = normalize_place(uf)
    if not uf_key or len(uf_key) != 2:
        raise ValueError("ANEEL territorial scope requires a two-letter UF")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "aneel-document"}, "invalid JSON")]
    if not isinstance(payload, dict) or not payload.get("success"):
        return [], [({"rowId": "aneel-document"}, "unexpected CKAN envelope")]
    result = payload.get("result")
    if not isinstance(result, dict) or not isinstance(result.get("records"), list):
        return [], [({"rowId": "aneel-document"}, "unexpected CKAN result")]
    counts: dict[str, dict[str, object]] = {}
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(result.get("records") or []):
        if not isinstance(item, dict):
            continue
        row_uf = normalize_place(str(item.get("SigUF") or ""))
        if row_uf != uf_key:
            continue
        ibge = str(item.get("CodMunicipio") or "").strip()
        raw_name = str(item.get("NomMunicipio") or "").strip()
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append(
                (
                    {
                        "rowId": f"aneel-indqual-{index}",
                        "territoryName": raw_name,
                        "uf": row_uf,
                        "ibgeCode": ibge,
                        "value": item.get("IdeConjUnidConsumidoras"),
                    },
                    "invalid IBGE municipality code",
                )
            )
            continue
        bucket = counts.setdefault(
            ibge,
            {"territoryName": raw_name or ibge, "uf": row_uf, "count": 0},
        )
        bucket["count"] = int(bucket["count"]) + 1
        if raw_name and not bucket["territoryName"]:
            bucket["territoryName"] = raw_name
    silver: list[dict] = []
    for ibge, bucket in sorted(counts.items(), key=lambda item: item[0]):
        silver.append(
            {
                "rowId": f"aneel-indqual-{ibge}-{competence}"[:64],
                "territoryName": str(bucket["territoryName"]),
                "uf": str(bucket["uf"]),
                "ibgeCode": ibge,
                "competence": competence,
                "transferName": "ANEEL_INDQUAL_MUNICIPIO",
                "value": int(bucket["count"]),
                "unit": "CONSUMER_UNIT_SETS",
            }
        )
    return silver, quarantined


def parse_anp_revendedores_api(
    body: bytes,
    *,
    uf: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    competence: str = "as_published",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse ANP revendedores JSON; aggregate by município+UF; drop CNPJ/PII."""
    uf_key = normalize_place(uf)
    if not uf_key or len(uf_key) != 2:
        raise ValueError("ANP territorial scope requires a two-letter UF")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "anp-document"}, "invalid JSON")]
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        return [], [({"rowId": "anp-document"}, "unexpected ANP envelope")]
    lookup = ibge_lookup or {}
    counts: dict[tuple[str, str], dict[str, object]] = {}
    for index, item in enumerate(payload.get("data") or []):
        if not isinstance(item, dict):
            continue
        row_uf = normalize_place(str(item.get("uf") or ""))
        if row_uf != uf_key:
            continue
        raw_name = str(item.get("municipio") or "").strip()
        if not raw_name:
            continue
        key = (normalize_place(raw_name), row_uf)
        bucket = counts.setdefault(
            key,
            {"territoryName": raw_name, "uf": row_uf, "count": 0, "index": index},
        )
        bucket["count"] = int(bucket["count"]) + 1
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for (place, place_uf), bucket in sorted(counts.items(), key=lambda item: item[0]):
        ibge = lookup.get((place, place_uf), "")
        row = {
            "rowId": f"anp-{place_uf.lower()}-{ibge or bucket['index']}-{competence}"[:64],
            "territoryName": str(bucket["territoryName"]),
            "uf": place_uf,
            "ibgeCode": ibge,
            "competence": competence,
            "transferName": "ANP_REVENDEDORES",
            "value": int(bucket["count"]),
            "unit": "ESTABLISHMENTS",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def _ms_municipality_name(raw: str) -> str:
    text = str(raw or "").strip()
    if normalize_place(text).startswith("PREFEITURA MUNICIPAL DE "):
        parts = text.split()
        if len(parts) >= 4:
            return " ".join(parts[3:]).strip()
    return text


_MS_TIPO_REPASSE = {
    "ICMS": "REPASSE DE ICMS",
    "IPVA": "REPASSE DE IPVA",
    "IPI": "REPASSE DE IPI EXPORTAÇÃO",
    "CIDE": "REPASSE DA CIDE",
}


def parse_state_ms_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "MS",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse MS CKAN datastore dump; filter Tipo_Repasse ICMS/IPVA/IPI/CIDE; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in _MS_TIPO_REPASSE:
        raise ValueError(f"unsupported state MS tax filter: {tax}")
    target = normalize_place(_MS_TIPO_REPASSE[tax_key])
    reader = csv.DictReader(io.StringIO(_decode_csv_bytes(body)))
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(reader):
        tipo = normalize_place(str(item.get("Tipo_Repasse") or ""))
        if tipo != target:
            continue
        raw_label = str(item.get("Municipio") or "").strip()
        raw_name = _ms_municipality_name(raw_label)
        ano_mes = str(item.get("Data") or "").strip()
        if len(ano_mes) == 6 and ano_mes.isdigit():
            competence = f"{ano_mes[:4]}-{ano_mes[4:]}"
        else:
            competence = ""
        amount_raw = item.get("Valor_Total")
        try:
            value = parse_brazilian_number(amount_raw)
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"ms-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(raw_name), normalize_place(uf)), "")
        row_token = str(item.get("_id") or index)
        row = {
            "rowId": f"ms-{tax_key.lower()}-{ibge or row_token}-{competence or 'na'}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not competence:
            quarantined.append((row, "missing competence YYYYMM"))
            continue
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_go_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "GO",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse GO CKAN datastore dump; IPVA only in published 2026 schema; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key != "IPVA":
        raise ValueError(f"unsupported state GO tax filter: {tax}")
    reader = csv.DictReader(io.StringIO(_decode_csv_bytes(body)))
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = "IPVA_QUOTA"
    for index, item in enumerate(reader):
        raw_name = str(item.get("DESC_MUN") or "").strip()
        ano_mes = str(item.get("NUMR_ANO_MES") or "").strip()
        if len(ano_mes) == 6 and ano_mes.isdigit():
            competence = f"{ano_mes[:4]}-{ano_mes[4:]}"
        else:
            competence = ""
        amount_raw = item.get("VALR_IPVA")
        try:
            value = float(str(amount_raw).strip().replace(",", "."))
        except (TypeError, ValueError):
            quarantined.append(
                (
                    {
                        "rowId": f"go-ipva-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    "non numeric IPVA amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(raw_name), normalize_place(uf)), "")
        row_token = str(item.get("_id") or index)
        row = {
            "rowId": f"go-ipva-{ibge or row_token}-{competence or 'na'}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence,
            "transferName": "IPVA",
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not competence:
            quarantined.append((row, "missing competence YYYYMM"))
            continue
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_pe_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "PE",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse PE municipal transfer CSV; publish zero IPVA as official; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA", "IPI"}:
        raise ValueError(f"unsupported state PE tax filter: {tax}")
    text = body.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    for index, item in enumerate(reader):
        raw_name = ""
        for key in item:
            if "MUNICIP" in normalize_place(key):
                raw_name = str(item.get(key) or "").strip()
                break
        if not raw_name:
            raw_name = str(item.get("MUNICÍPIO") or item.get("MUNICIPIO") or "").strip()
        year = str(item.get("ano") or item.get("ANO") or "").strip()
        month = str(item.get("mes") or item.get("Mês") or item.get("Mes") or "").strip().zfill(2)
        amount_raw = None
        for key in item:
            if normalize_place(key) == tax_key:
                amount_raw = item.get(key)
                break
        if amount_raw is None:
            quarantined.append(
                (
                    {
                        "rowId": f"pe-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                    },
                    f"missing {tax_key} column",
                )
            )
            continue
        try:
            value = float(str(amount_raw).strip().replace(",", "."))
        except ValueError:
            quarantined.append(
                (
                    {
                        "rowId": f"pe-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(raw_name), normalize_place(uf)), "")
        row = {
            "rowId": f"pe-{tax_key.lower()}-{ibge or index}-{year}-{month}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": f"{year}-{month}"[:7],
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_ba_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "BA",
    competence: str = "2024",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse BA multi-header semicolon CSV; monthly ICMS/IPI/IPVA columns; no credit."""
    tax_key = str(tax or "").strip().upper()
    amount_indexes = {"ICMS": 4, "IPI": 9, "IPVA": 13}
    if tax_key not in amount_indexes:
        raise ValueError(f"unsupported state BA tax filter: {tax}")
    amount_index = amount_indexes[tax_key]
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = body.decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    competence_key = str(competence or "2024").strip()[:7]
    for index, item in enumerate(reader):
        if not item:
            continue
        raw_name = str(item[0] or "").strip()
        if not raw_name:
            continue
        place = normalize_place(raw_name)
        joined = normalize_place(";".join(item[:8]))
        if place.startswith("DENOMINACAO") or "ICMS" in joined and index == 0:
            continue
        if place.startswith("PAGINA") or place.startswith("TOTAL"):
            continue
        if len(item) <= amount_index:
            quarantined.append(
                (
                    {
                        "rowId": f"ba-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                    },
                    f"missing {tax_key} column",
                )
            )
            continue
        amount_raw = item[amount_index]
        try:
            value = parse_brazilian_number(amount_raw)
        except ValueError:
            quarantined.append(
                (
                    {
                        "rowId": f"ba-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(raw_name), normalize_place(uf)), "")
        row = {
            "rowId": f"ba-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_state_sc_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "SC",
    competence_year: str = "2017",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEF/SC Anual CSV (latin-1, `;`); TOTAL ICMS/IPI/IPVA; no credit."""
    tax_key = str(tax or "").strip().upper()
    amount_indexes = {"ICMS": 7, "IPI": 9, "IPVA": 10}
    if tax_key not in amount_indexes:
        raise ValueError(f"unsupported state SC tax filter: {tax}")
    amount_index = amount_indexes[tax_key]
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = body.decode("latin-1")
    reader = csv.reader(io.StringIO(text), delimiter=";")
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    modality = f"{tax_key}_QUOTA"
    competence_key = str(competence_year or "2017").strip()[:4]
    for index, item in enumerate(reader):
        if not item or len(item) <= 1:
            continue
        sef_code = str(item[0] or "").strip()
        if not sef_code.isdigit():
            continue
        raw_name = str(item[1] or "").strip()
        if not raw_name:
            continue
        if len(item) <= amount_index:
            quarantined.append(
                (
                    {
                        "rowId": f"sc-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "sefCode": sef_code,
                    },
                    f"missing {tax_key} column",
                )
            )
            continue
        amount_raw = item[amount_index]
        try:
            value = parse_brazilian_number(amount_raw)
        except ValueError:
            quarantined.append(
                (
                    {
                        "rowId": f"sc-{tax_key.lower()}-{index}",
                        "territoryName": raw_name,
                        "uf": uf,
                        "sefCode": sef_code,
                        "value": amount_raw,
                    },
                    f"non numeric {tax_key} amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(raw_name), normalize_place(uf)), "")
        row = {
            "rowId": f"sc-{tax_key.lower()}-{ibge or index}-{competence_key}"[:64],
            "territoryName": raw_name,
            "uf": uf,
            "ibgeCode": ibge,
            "sefCode": sef_code,
            "competence": competence_key,
            "transferName": tax_key,
            "modality": modality,
            "value": value,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def _tesouro_coint_blank_amount(raw: object) -> bool:
    text = str(raw or "").strip()
    if not text:
        return True
    compact = re.sub(r"\s+", "", text)
    return compact in {"-", "–", "—", ".", ".."}


def _tesouro_transfer_family(name: str) -> str:
    mapping = {
        "FPM": "FPM",
        "ITR": "ITR",
        "IPI-EXP": "IPI_EXP",
        "IPI-Exp": "IPI_EXP",
        "Royalties": "ROYALTY",
        "LC176": "LC176",
        "LC 176/2020": "LC176",
        "LC 176/2020 (ADO25)": "LC176",
        "IOF-Ouro": "IOF_OURO",
        "IOF Ouro": "IOF_OURO",
        "IOF": "IOF_OURO",
        "FUNDEB-COMPLEMENT": "FDB_COMP",
        "FDB-COMP": "FDB_COMP",
        "FUNDEB": "FUNDEB",
        "AJUSTE FUNDEB": "AJUSTE_FUNDEB",
        "CIDE": "CIDE",
        "CIDE-Combustíveis": "CIDE",
        "CIDE-Combustiveis": "CIDE",
        "FEX": "FEX",
        "LC87": "LC87",
        "LC 87/96": "LC87",
        "LC87/96": "LC87",
    }
    if name in mapping:
        return mapping[name]
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")
    return cleaned.upper() or "TRANSFER"


def parse_tesouro_monthly_csv(
    body: bytes,
    *,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    item_allowlist: list[str] | tuple[str, ...] | None = None,
    destination_allowlist: list[str] | tuple[str, ...] | None = None,
    transfer_name: str | None = None,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse Tesouro CKAN monthly CSV for an allowlisted transfer family.

    Defaults preserve FPM behavior. Royalties match Transferência=Royalties
    (Item may be FEP/CFEM/ANP/…). IPI-EXP rows in recent files are often
    FUNDEB retention only; still published as occurrence, never credit.
    """
    items = {str(value).strip() for value in (item_allowlist or ()) if str(value).strip()}
    destinations = {
        str(value).strip() for value in (destination_allowlist or ()) if str(value).strip()
    }
    if not items and not destinations:
        items = {"FPM"}
    family_label = (
        transfer_name
        or (next(iter(destinations)) if destinations and not items else None)
        or (next(iter(items)) if items else "TRANSFER")
    )
    family_key = _tesouro_transfer_family(family_label)
    text = body.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(reader):
        name = str(item.get("Município") or item.get("Municipio") or "").strip()
        uf = str(item.get("UF") or "").strip()
        year = str(item.get("ANO") or "").strip()
        month = str(item.get("Mês") or item.get("Mes") or "").zfill(2)
        item_name = str(
            item.get("Item transferência") or item.get("Item transferencia") or ""
        ).strip()
        destination = str(item.get("Transferência") or item.get("Transferencia") or "").strip()
        matched = (bool(items) and item_name in items) or (
            bool(destinations) and destination in destinations
        )
        if not matched:
            # Legacy FPM: also keep rows whose destination is the allowlisted item.
            if items and destination in items:
                matched = True
        if not matched:
            continue
        amounts = []
        for key in item:
            if "Dec" in key or "dec" in key:
                try:
                    amounts.append(float(str(item[key]).replace(",", ".")))
                except ValueError:
                    amounts.append(None)
        prefix = family_key.lower()
        if not amounts or any(value is None for value in amounts):
            quarantined.append(
                (
                    {"rowId": f"{prefix}-{index}", "territoryName": name, "uf": uf},
                    f"non numeric {family_label} amount",
                )
            )
            continue
        total = float(sum(value for value in amounts if value is not None))
        ibge = lookup.get((normalize_place(name), normalize_place(uf)), "")
        if destinations and destination in destinations:
            modality = f"{family_key}_RECEIVED"
        elif item_name == destination or destination == family_label:
            modality = f"{family_key}_RECEIVED"
        else:
            dest_key = _tesouro_transfer_family(destination)
            modality = f"{family_key}_TO_{dest_key}"
        row = {
            "rowId": f"{prefix}-{ibge or index}-{year}-{month}-{modality}-{item_name}"[:64],
            "territoryName": name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": f"{year}-{month}"[:7],
            "transferName": family_label,
            "modality": modality,
            "itemName": item_name,
            "destination": destination,
            "value": total,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
    return silver, quarantined


def parse_tesouro_coint_municipio_csv(
    body: bytes,
    *,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    transfer_name: str = "CIDE",
    competence: str | None = None,
    max_rows: int | None = None,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse Tesouro COINT wide CSV (CIDE/FEX por município).

    Layout: COD_MUN;Município;UF;Município - UF;Mês;YYYY... with BR amounts.
    COD_MUN is not IBGE7 — join municipality+UF via SICONFI/entes. Empty or
    dash cells are skipped (not published as zero). Explicit 0 is kept.
    """
    family_label = str(transfer_name or "TRANSFER").strip() or "TRANSFER"
    family_key = _tesouro_transfer_family(family_label)
    competence_key = str(competence or "").strip()[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", competence_key):
        raise ValueError("tesouro_coint_municipio_csv requires competence YYYY-MM")
    year_filter = competence_key[:4]
    month_filter = str(int(competence_key[5:7]))
    limit = int(max_rows) if max_rows is not None else None
    if limit is not None and limit <= 0:
        raise ValueError("max_rows must be a positive integer when set")
    text = body.decode("latin-1")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    if not reader.fieldnames or year_filter not in reader.fieldnames:
        return [], [({"rowId": "document"}, f"missing year column {year_filter}")]
    lookup = ibge_lookup or {}
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(reader):
        month_raw = str(item.get("Mês") or item.get("Mes") or "").strip()
        try:
            month_num = str(int(month_raw))
        except ValueError:
            continue
        if month_num != month_filter:
            continue
        raw_amount = item.get(year_filter)
        if _tesouro_coint_blank_amount(raw_amount):
            continue
        name = str(item.get("Município") or item.get("Municipio") or "").strip()
        uf = str(item.get("UF") or "").strip()
        try:
            value = parse_brazilian_number(raw_amount)
        except ValueError:
            quarantined.append(
                (
                    {"rowId": f"{family_key.lower()}-{index}", "territoryName": name, "uf": uf},
                    f"non numeric {family_label} amount",
                )
            )
            continue
        ibge = lookup.get((normalize_place(name), normalize_place(uf)), "")
        modality = f"{family_key}_RECEIVED"
        row = {
            "rowId": f"{family_key.lower()}-{ibge or index}-{competence_key}-{modality}"[:64],
            "territoryName": name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": competence_key,
            "transferName": family_label,
            "modality": modality,
            "value": value,
            "unit": "BRL",
            "codMun": str(item.get("COD_MUN") or "").strip(),
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "missing IBGE municipality code"))
            continue
        silver.append(row)
        if limit is not None and len(silver) >= limit:
            break
    return silver, quarantined


def parse_siconfi_statement(
    body: bytes, *, dataset: str = "RREO"
) -> tuple[list[dict], list[tuple[dict, str]]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [], [({"rowId": "document"}, "invalid JSON")]
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return [], [({"rowId": "document"}, "unexpected SICONFI envelope")]
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    for index, item in enumerate(items):
        ibge = str(item.get("cod_ibge") or "").strip()
        competence = str(item.get("exercicio") or "").strip()
        account = str(item.get("cod_conta") or item.get("conta") or "").strip()
        raw = item.get("valor")
        row = {
            "rowId": f"{ibge}-{competence}-{account}-{index}"[:64],
            "ibgeCode": ibge,
            "competence": competence,
            "account": account,
            "annex": item.get("anexo"),
            "column": item.get("coluna"),
            "dataset": dataset,
            "value": raw,
            "unit": "BRL",
        }
        if not IBGE_MUNICIPALITY.fullmatch(ibge):
            quarantined.append((row, "invalid IBGE municipality code"))
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            quarantined.append((row, "non numeric statement value"))
            continue
        silver.append({**row, "value": value})
    return silver, quarantined
