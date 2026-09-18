from tests.helpers.tokens import auth_headers, issue_token

from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_BETA,
    PURPOSE_ALPHA_ACTIVE,
    PURPOSE_ALPHA_EXPIRED,
    PURPOSE_BETA_ACTIVE,
    TENANT_ALPHA,
    TENANT_BETA,
    TERRITORY_ALPHA_CENTRO,
    TERRITORY_ALPHA_NORTE,
    TERRITORY_BETA_SEDE,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
    USER_ANALYST_BETA,
)
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.entrypoints.main import create_app


def _analyst_headers(**kwargs):
    data = dict(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    data.update(kwargs)
    return auth_headers(**data)


def test_protected_routes_require_access_context_dependency() -> None:
    app = create_app()
    protected = []
    for route in app.routes:
        original = getattr(route, "original_router", None)
        nested = original.routes if original is not None else [route]
        for item in nested:
            path = getattr(item, "path", "")
            if path.startswith("/v1"):
                protected.append(item)
    assert protected
    for route in protected:
        dependant = getattr(route, "dependant", None)
        assert dependant is not None, getattr(route, "path", route)
        dependency_calls = [dep.call for dep in dependant.dependencies]
        assert get_access_context in dependency_calls, route.path


def test_missing_token_returns_401(api_client) -> None:
    response = api_client.get("/v1/tax-credits")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")


def test_missing_purpose_returns_403(api_client) -> None:
    token = issue_token(subject=USER_ANALYST_ALPHA, tenant_id=TENANT_ALPHA)
    response = api_client.get(
        "/v1/tax-credits",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Territory-Id": str(TERRITORY_ALPHA_CENTRO),
        },
    )
    assert response.status_code == 403
    assert "purpose" in response.json()["detail"].lower()


def test_expired_purpose_returns_403(api_client) -> None:
    response = api_client.get(
        "/v1/tax-credits",
        headers=_analyst_headers(purpose_id=PURPOSE_ALPHA_EXPIRED),
    )
    assert response.status_code == 403
    assert "expired" in response.json()["detail"].lower()


def test_denied_territory_returns_403(api_client) -> None:
    response = api_client.get(
        "/v1/tax-credits",
        headers=_analyst_headers(territory_id=TERRITORY_ALPHA_NORTE),
    )
    assert response.status_code == 403
    assert "territory" in response.json()["detail"].lower()


def test_tech_admin_cannot_read_fiscal_content(api_client) -> None:
    response = api_client.get(
        "/v1/tax-credits",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
    assert "fiscal" in response.json()["detail"].lower()


def test_cross_tenant_credit_is_hidden(api_client) -> None:
    response = api_client.get(
        f"/v1/tax-credits/{CREDIT_BETA}",
        headers=_analyst_headers(),
    )
    assert response.status_code == 404


def test_beta_analyst_cannot_list_alpha_credits(api_client) -> None:
    response = api_client.get(
        "/v1/tax-credits",
        headers=auth_headers(
            subject=USER_ANALYST_BETA,
            tenant_id=TENANT_BETA,
            territory_id=TERRITORY_BETA_SEDE,
            purpose_id=PURPOSE_BETA_ACTIVE,
        ),
    )
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["items"]]
    assert str(CREDIT_BETA) in ids
    assert all(item["tenantId"] == str(TENANT_BETA) for item in response.json()["items"])


def test_collection_is_not_implemented(api_client) -> None:
    headers = _analyst_headers()
    credit_list = api_client.get("/v1/tax-credits", headers=headers)
    credit_id = credit_list.json()["items"][0]["id"]
    collection = api_client.post(f"/v1/tax-credits/{credit_id}/collection-cases", headers=headers)
    assert collection.status_code == 404
