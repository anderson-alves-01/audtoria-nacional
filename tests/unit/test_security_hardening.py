from sirta_api.config import Settings
from sirta_api.domain.dlp import DlpDecision, scan_prompt
from sirta_api.domain.errors import ForbiddenError
from sirta_api.domain.security_policy import ensure_mfa_if_required, token_has_mfa


def test_mfa_not_required_in_local_environment() -> None:
    ensure_mfa_if_required({"sub": "u1"}, environment="local")


def test_mfa_required_outside_local_without_claim() -> None:
    try:
        ensure_mfa_if_required({"sub": "u1"}, environment="staging")
        raised = False
    except ForbiddenError as exc:
        raised = True
        assert "MFA" in exc.detail or "mfa" in exc.detail.lower()
    assert raised is True


def test_mfa_accepted_via_amr_or_acr() -> None:
    assert token_has_mfa({"amr": ["pwd", "mfa"]}) is True
    assert token_has_mfa({"acr": "urn:mace:incommon:iap:silver"}) is False
    assert token_has_mfa({"acr": "https://refeds.org/profile/mfa"}) is True
    assert token_has_mfa({"mfa": True}) is True
    ensure_mfa_if_required({"amr": ["otp", "mfa"]}, environment="prod")


def test_dlp_blocks_cpf_cnpj_and_bearer_like_secrets() -> None:
    clean = scan_prompt("Qual a competência do FPM em 2026?")
    assert clean.allowed is True
    assert clean.decision is DlpDecision.ALLOW

    cpf = scan_prompt("Contribuinte CPF 529.982.247-25 pediu revisão")
    assert cpf.allowed is False
    assert cpf.decision is DlpDecision.BLOCK
    assert "cpf" in cpf.reason.lower() or "personal" in cpf.reason.lower()

    secret = scan_prompt("use Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.abc.def")
    assert secret.allowed is False


def test_non_local_settings_reject_embedded_local_secrets(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("S3_SECRET_KEY", raising=False)
    try:
        Settings(_env_file=None)
        raised = False
    except Exception:
        raised = True
    assert raised is True
