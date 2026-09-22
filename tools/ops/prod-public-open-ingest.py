"""Authorized PUBLIC_OPEN reference ingest against PROD ALB (no credit)."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

import jwt

from sirta_api.adapters.db.synthetic_ids import (
    AUDIENCE,
    ISSUER,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
)

BASE = "http://sirta-prod-alb-1369017354.sa-east-1.elb.amazonaws.com"
EVIDENCE = ROOT / "evidence" / "ops" / "prod-public-open-ingest.txt"

# Minimum set for Executivo / Financeiro / Transferências charts.
SOURCES = [
    "IBGE-SIDRA",
    "IBGE-SIDRA-PIB",
    "IBGE-SIDRA-CEMP",
    "SICONFI-ENTES",
    "TESOURO-TRANSPARENTE",
    "TESOURO-FPM-VALORES",
]


def admin_headers() -> dict[str, str]:
    key = (ROOT / "tests" / "fixtures" / "jwt" / "private.pem").read_bytes()
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(USER_ADMIN_ALPHA),
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + timedelta(hours=6),
            "tenant_id": str(TENANT_ALPHA),
            "amr": ["pwd", "mfa"],
        },
        key,
        algorithm="RS256",
        headers={"kid": "sirta-test"},
    )
    return {
        "Authorization": f"Bearer {token}",
        "X-Territory-Id": str(TERRITORY_ALPHA_CENTRO),
        "X-Purpose-Id": str(PURPOSE_ALPHA_ACTIVE),
        "Content-Type": "application/json",
    }


def request_json(method: str, path: str, headers: dict[str, str], timeout: int = 600) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        method=method,
        headers=headers,
        data=b"{}" if method == "POST" else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw[:2000]}
        return exc.code, payload


def main() -> int:
    lines: list[str] = [
        f"started={datetime.now(UTC).isoformat()}",
        "authorization=PUBLIC_OPEN_REFERENCE_ONLY_PROD",
        "account=332380491162",
        "region=sa-east-1",
        "createsTaxCredit=false",
    ]
    headers = admin_headers()
    for source_id in SOURCES:
        print(f"INGEST {source_id} ...", flush=True)
        t0 = time.time()
        status, body = request_json("POST", f"/v1/data-sources/{source_id}/ingest", headers)
        elapsed = round(time.time() - t0, 1)
        summary = {
            "sourceId": source_id,
            "httpStatus": status,
            "elapsedSec": elapsed,
            "runId": body.get("runId"),
            "status": body.get("status"),
            "replay": body.get("replay"),
            "receivedCount": body.get("receivedCount"),
            "silverCount": body.get("silverCount"),
            "quarantinedCount": body.get("quarantinedCount"),
            "taxCreditCreated": body.get("taxCreditCreated"),
            "homologationStatus": body.get("homologationStatus"),
            "title": body.get("title"),
            "detail": body.get("detail"),
        }
        line = json.dumps(summary, ensure_ascii=True)
        print(line, flush=True)
        lines.append(line)
        if status >= 400:
            lines.append(f"FAILED_SOURCE={source_id}")
            EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return 1

    # analyst-readable gold check via public-open session
    sess_status, sess = request_json("GET", "/v1/auth/public-open-session", {})
    if sess_status != 200:
        lines.append(f"session_failed={sess_status}")
        EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 1
    read_headers = {
        "Authorization": f"Bearer {sess['accessToken']}",
        "X-Territory-Id": sess["territoryId"],
        "X-Purpose-Id": sess["purposeId"],
    }
    g_status, gold = request_json("GET", "/v1/indicators/official-gold", read_headers)
    lines.append(
        json.dumps(
            {
                "goldHttp": g_status,
                "published": gold.get("published"),
                "itemCount": len(gold.get("items") or []),
                "emptyCount": len(gold.get("emptySources") or []),
                "createsTaxCredit": gold.get("createsTaxCredit"),
            },
            ensure_ascii=True,
        )
    )
    for dash in ("executivo", "financeiro", "transferencias"):
        d_status, dash_body = request_json("GET", f"/v1/dashboards/{dash}", read_headers)
        lines.append(
            json.dumps(
                {
                    "dashboard": dash,
                    "http": d_status,
                    "published": dash_body.get("published"),
                    "items": len(dash_body.get("items") or []),
                    "kpis": len(dash_body.get("kpis") or []),
                    "charts": len(dash_body.get("charts") or []),
                },
                ensure_ascii=True,
            )
        )
    lines.append(f"finished={datetime.now(UTC).isoformat()}")
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"EVIDENCE={EVIDENCE}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
