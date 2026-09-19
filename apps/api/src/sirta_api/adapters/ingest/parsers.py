from __future__ import annotations

import csv
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
