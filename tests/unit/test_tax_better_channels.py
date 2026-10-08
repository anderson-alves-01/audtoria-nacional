import csv
import io
from decimal import Decimal

from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.domain.catalog import ingest_allowed
from sirta_api.domain.tax_better import IntakeConfigError, read_configured_intake

FIELD_MAP = {
    "organ": "orgao",
    "tax": "imposto",
    "fgo": "fgo",
    "operationValue": "op_valor",
    "operationBase": "op_base",
    "operationTax": "op_imposto",
    "malhaValue": "malha_valor",
    "malhaBase": "malha_base",
    "malhaTax": "malha_imposto",
}

ROWS = [
    {
        "orgao": "DETRAN",
        "imposto": "ICMS",
        "fgo": "VENDA PJ",
        "op_valor": "100",
        "op_base": "80",
        "op_imposto": "10",
        "malha_valor": "90",
        "malha_base": "80",
        "malha_imposto": "9",
        "cidade": "BSB",
    },
    {
        "orgao": "DETRAN",
        "imposto": "ICMS",
        "fgo": "VENDA PJ",
        "op_valor": "50",
        "op_base": "40",
        "op_imposto": "5",
        "malha_valor": "40",
        "malha_base": "40",
        "malha_imposto": "4",
        "cidade": "BSB",
    },
]


def test_file_layout_and_api_body_build_the_same_vision():
    file_text = _csv(ROWS)
    from_file = read_configured_intake(
        {"channel": "file", "fieldMap": FIELD_MAP},
        file_text=file_text,
    )
    from_api = read_configured_intake(
        {"channel": "api", "fieldMap": FIELD_MAP, "secretName": "DETRAN_API_KEY", "endpoint": "https://example.invalid"},
        api_rows=ROWS,
    )
    assert from_file["createsTaxCredit"] is False
    assert from_api["vision"] == from_file["vision"]
    assert from_file["vision"]["rows"][0]["operacao"]["valor"] == Decimal("150")
    assert from_file["vision"]["rows"][0]["variables"]["cidade"] == "BSB"
    assert from_file["accepted"][0]["approved"] is False
    assert "4000000" not in str(from_file)


def test_missing_measure_is_quarantined_and_left_out_of_the_vision():
    rows = [dict(ROWS[0]), dict(ROWS[1])]
    rows[1]["op_valor"] = ""
    result = read_configured_intake(
        {"channel": "file", "fieldMap": FIELD_MAP},
        file_text=_csv(rows),
    )
    assert result["quarantined"] == [{"row": 2, "reason": "campo obrigatório ausente"}]
    assert result["vision"]["rows"][0]["operacao"]["valor"] == Decimal("100")


def test_file_without_layout_and_api_without_secret_are_refused():
    incomplete = {"channel": "file", "fieldMap": {"organ": "orgao"}}
    try:
        read_configured_intake(incomplete, file_text=_csv(ROWS))
        raise AssertionError("layout should be required")
    except IntakeConfigError as exc:
        assert "leiaute" in str(exc).casefold()
    try:
        read_configured_intake(
            {"channel": "api", "fieldMap": FIELD_MAP, "secretName": " "},
            api_rows=ROWS,
        )
        raise AssertionError("secret name should be required")
    except IntakeConfigError as exc:
        assert "segredo" in str(exc).casefold()


def test_template_source_stays_restricted_and_does_not_fetch_an_organ():
    source = catalog_source("TAX-BETTER-ENTRADA")
    assert source is not None
    assert source["connector"] == "tax_better_intake"
    assert source["access_classification"] == "RESTRICTED"
    assert source["status"] == "CREDENTIAL_REQUIRED"
    assert source["endpoint"] == "none"
    assert ingest_allowed(
        source_role=source["source_role"],
        access_classification=source["access_classification"],
        status=source["status"],
        fixture_kind=source["fixture_kind"],
    ) is False


def _csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
