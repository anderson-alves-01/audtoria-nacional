"""Load the public SPED NF-e UF x CFOP workbook (source SPED-NFE-UF-CFOP).

Default is --dry-run: parse, reconcile, compute sha256 and write a report. No network, no
database, no credentials. --execute needs --confirm <sha256 of the file> and --expect-tenant
<uuid>. It signs in with SIRTA_OPERATOR_USER and SIRTA_OPERATOR_PASSWORD from the
environment (never written anywhere), uploads once and reads the result back.
The load is idempotent by tenant, checksum and layout; repeating it returns a replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from sirta_api.adapters.ingest.sped_xlsx import SpedLayoutError, parse_sped_workbook  # noqa: E402
from sirta_api.domain.sped_operations import (  # noqa: E402
    SPED_LAYOUT_VERSION,
    SPED_SOURCE_ID,
    reconcile,
)

DEFAULT_FILE = ROOT / "docs" / "data" / "Consolidado_Operacoes_UF_2021_2025_SPED.xlsx"
DEFAULT_BASE = "http://sirta-prod-alb-1369017354.sa-east-1.elb.amazonaws.com"
EVIDENCE_DIR = ROOT / "evidence" / "ops"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def local_summary(body: bytes) -> tuple[dict, list[str]]:
    digest = hashlib.sha256(body).hexdigest()
    workbook = parse_sped_workbook(body)
    report = reconcile(workbook)
    quantity = sum(row.quantity for row in workbook.serie)
    known_values = [
        row.estimated_value for row in workbook.serie if row.estimated_value is not None
    ]
    summary = {
        "sha256": digest,
        "sizeBytes": len(body),
        "layoutVersion": SPED_LAYOUT_VERSION,
        "seriesRows": report.series_rows,
        "baseLines": report.base_rows,
        "baseFacts": report.base_facts,
        "consolidatedCells": report.consolidated_cells,
        "serieQuantitySum": quantity,
        "serieRowsWithoutValue": report.series_rows - len(known_values),
        "maxValueDifference": str(report.max_value_difference),
        "classificationMismatches": report.classification_mismatches,
        "reconciliationOk": report.ok,
    }
    return summary, report.errors + report.warnings


def call(
    method: str, url: str, *, headers: dict[str, str], data: bytes | None = None
) -> tuple[int, dict]:
    request = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw[:500]}


def write_report(name: str, lines: list[str]) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def dry_run(body: bytes, file: Path) -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        f"started={datetime.now(UTC).isoformat()}",
        "mode=DRY_RUN network=false database=false credentials=false",
        f"sourceId={SPED_SOURCE_ID}",
        f"file={file.name}",
    ]
    try:
        summary, messages = local_summary(body)
    except SpedLayoutError as exc:
        lines.append(f"layoutError={exc}")
        path = write_report(f"sped-nfe-uf-cfop-dryrun-{stamp}.txt", lines)
        print(f"LAYOUT ERROR: {exc}\nreport={path}")
        return 1
    lines.extend(f"{key}={value}" for key, value in summary.items())
    lines.extend(f"note={message}" for message in messages)
    path = write_report(f"sped-nfe-uf-cfop-dryrun-{stamp}.txt", lines)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"report={path}")
    return 0 if summary["reconciliationOk"] else 1


def login(base: str) -> dict:
    user = os.environ.get("SIRTA_OPERATOR_USER", "")
    password = os.environ.get("SIRTA_OPERATOR_PASSWORD", "")
    if not user or not password:
        raise SystemExit("Set SIRTA_OPERATOR_USER and SIRTA_OPERATOR_PASSWORD in the environment.")
    status, body = call(
        "POST",
        f"{base}/v1/auth/login",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"username": user, "password": password}).encode("utf-8"),
    )
    if status != 200 or "accessToken" not in body:
        raise SystemExit(f"Login refused (HTTP {status}).")
    return body


def execute(body: bytes, file: Path, *, base: str, confirm: str, expect_tenant: str) -> int:
    summary, _messages = local_summary(body)
    if not summary["reconciliationOk"]:
        print("Local reconciliation failed. Nothing was sent.")
        return 1
    if confirm != summary["sha256"]:
        print("--confirm does not match the sha256 of the file. Nothing was sent.")
        return 1
    session = login(base)
    if session["tenantId"] != expect_tenant:
        print("Signed-in tenant differs from --expect-tenant. Nothing was sent.")
        return 1
    if session["role"] != "tech_admin":
        print("The signed-in user is not the technical administrator. Nothing was sent.")
        return 1
    scope = {
        "Authorization": f"Bearer {session['accessToken']}",
        "X-Territory-Id": session["territoryId"],
        "X-Purpose-Id": session["purposeId"],
    }
    lines = [
        f"started={datetime.now(UTC).isoformat()}",
        "mode=EXECUTE authorization=SPED_PUBLIC_AGGREGATED_PROD",
        f"base={base}",
        f"sourceId={SPED_SOURCE_ID}",
        f"tenantId={session['tenantId']}",
        f"territoryId={session['territoryId']}",
        f"sha256={summary['sha256']}",
        "createsTaxCredit=false homologated=false published=false",
    ]
    status, upload = call(
        "POST",
        f"{base}/v1/data-sources/{SPED_SOURCE_ID}/upload",
        headers={**scope, "Content-Type": XLSX},
        data=body,
    )
    lines.append(
        json.dumps(
            {
                "uploadHttp": status,
                "runId": upload.get("runId"),
                "status": upload.get("status"),
                "replay": upload.get("replay"),
                "receivedCount": upload.get("receivedCount"),
                "silverCount": upload.get("silverCount"),
                "quarantinedCount": upload.get("quarantinedCount"),
                "checksum": upload.get("checksum"),
                "detail": upload.get("detail"),
            },
            ensure_ascii=True,
        )
    )
    ok = status == 200 and upload.get("status") == "VALIDATED"
    if ok:
        read_status, read = call(
            "GET", f"{base}/v1/sped-operacoes?level=SERIE&pageSize=1000", headers=scope
        )
        items = read.get("items") or []
        read_quantity = sum(int(item["quantidade"]) for item in items)
        missing_values = sum(1 for item in items if item["valorEstimado"] is None)
        check = {
            "readHttp": read_status,
            "total": read.get("total"),
            "quantitySum": read_quantity,
            "rowsWithoutValue": missing_values,
            "runId": (read.get("run") or {}).get("runId"),
            "valueKind": read.get("valueKind"),
            "homologated": read.get("homologated"),
            "published": read.get("published"),
            "createsTaxCredit": read.get("createsTaxCredit"),
        }
        lines.append(json.dumps(check, ensure_ascii=True))
        ok = (
            read_status == 200
            and read.get("total") == summary["seriesRows"]
            and read_quantity == summary["serieQuantitySum"]
            and missing_values == summary["serieRowsWithoutValue"]
            and check["runId"] == upload.get("runId")
        )
        lines.append(f"readBackMatchesFile={ok}")
    lines.append(f"finished={datetime.now(UTC).isoformat()} ok={ok}")
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    path = write_report(f"prod-sped-ingest-{stamp}.txt", lines)
    print("\n".join(line for line in lines if "accessToken" not in line))
    print(f"report={path}")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--base", default=DEFAULT_BASE)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--confirm", default="", help="sha256 of the file (required with --execute)"
    )
    parser.add_argument("--expect-tenant", default="", help="tenant UUID (required with --execute)")
    args = parser.parse_args()
    if not args.file.is_file():
        print(f"File not found: {args.file}")
        return 2
    body = args.file.read_bytes()
    if not args.execute:
        return dry_run(body, args.file)
    if not args.confirm or not args.expect_tenant:
        print("--execute requires --confirm <sha256> and --expect-tenant <uuid>.")
        return 2
    return execute(
        body,
        args.file,
        base=args.base.rstrip("/"),
        confirm=args.confirm,
        expect_tenant=args.expect_tenant,
    )


if __name__ == "__main__":
    sys.exit(main())
