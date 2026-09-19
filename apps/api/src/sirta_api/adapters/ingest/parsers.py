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
    if tax_key not in {"ICMS", "IPVA"}:
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
    # Official layout: Município | ICMS Total/Líquido/FUNDEB | IPVA Total/...
    amount_col = 1 if tax_key == "ICMS" else 4
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


def parse_state_rs_xls(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "RS",
    competence: str = "2025-01",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse SEFAZ-RS MontaArquivo monthly XLS; ICMS TOTAL month REPASSE / IPVA Total Mês."""
    try:
        import xlrd
        from xlrd.biffh import XLRDError
    except ImportError as exc:  # pragma: no cover - dependency declared in pyproject
        raise RuntimeError("xlrd is required for state_rs_xls") from exc
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA"}:
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

    if tax_key == "ICMS":
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
            or place.startswith("SAC ")
            or place.startswith("OUVIDORIA")
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
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state MG tax filter: {tax}")
    amount_field = "vr_icms" if tax_key == "ICMS" else "vr_ipva"
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
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state ES tax filter: {tax}")
    amount_field = "IcmsTotal" if tax_key == "ICMS" else "Ipva"
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


def parse_state_ms_csv(
    body: bytes,
    *,
    tax: str,
    ibge_lookup: dict[tuple[str, str], str] | None = None,
    uf: str = "MS",
) -> tuple[list[dict], list[tuple[dict, str]]]:
    """Parse MS CKAN datastore dump; filter Tipo_Repasse ICMS/IPVA; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state MS tax filter: {tax}")
    target = normalize_place(f"REPASSE DE {tax_key}")
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
    if tax_key not in {"ICMS", "IPVA"}:
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
    """Parse BA multi-header semicolon CSV; monthly ICMS/IPVA columns; no credit."""
    tax_key = str(tax or "").strip().upper()
    if tax_key not in {"ICMS", "IPVA"}:
        raise ValueError(f"unsupported state BA tax filter: {tax}")
    amount_index = 4 if tax_key == "ICMS" else 13
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


def parse_tesouro_monthly_csv(
    body: bytes, *, ibge_lookup: dict[tuple[str, str], str] | None = None
) -> tuple[list[dict], list[tuple[dict, str]]]:
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
        if item_name != "FPM" and destination != "FPM":
            continue
        amounts = []
        for key in item:
            if "Dec" in key or "dec" in key:
                try:
                    amounts.append(float(str(item[key]).replace(",", ".")))
                except ValueError:
                    amounts.append(None)
        if not amounts or any(value is None for value in amounts):
            quarantined.append(
                (
                    {"rowId": f"fpm-{index}", "territoryName": name, "uf": uf},
                    "non numeric FPM amount",
                )
            )
            continue
        total = float(sum(value for value in amounts if value is not None))
        ibge = lookup.get((normalize_place(name), normalize_place(uf)), "")
        if item_name == "FPM" and destination == "FPM":
            modality = "FPM_RECEIVED"
        else:
            modality = f"FPM_TO_{destination}"
        row = {
            "rowId": f"fpm-{ibge or index}-{year}-{month}-{modality}"[:64],
            "territoryName": name,
            "uf": uf,
            "ibgeCode": ibge,
            "competence": f"{year}-{month}"[:7],
            "transferName": "FPM",
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
