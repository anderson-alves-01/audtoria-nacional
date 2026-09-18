from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def test_logs_redact_bearer_token_and_personal_identifiers(api_client, capsys) -> None:
    headers = auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    headers["X-Debug-Cpf"] = "123.456.789-00"
    response = api_client.get("/v1/tax-credits", headers=headers)
    assert response.status_code == 200
    captured = capsys.readouterr().out + capsys.readouterr().err
    token = headers["Authorization"].split(" ", 1)[1]
    assert token not in captured
    assert "123.456.789-00" not in captured
    assert "Bearer [REDACTED]" in captured or "authorization" not in captured.lower()
