"""Unit tests for RFB territorial scope, resume and EI policy."""

from sirta_api.adapters.ingest.rfb_cnpj import parse_rfb_estabelecimentos
from sirta_api.domain.errors import ForbiddenError
from sirta_api.domain.rfb_cnpj import (
    ResumeCursor,
    assert_territorial_scope_ready,
    build_rfb_landing_manifest,
    build_rfb_readiness,
    ei_policy_decision,
    next_resume_plan,
    parse_territorial_scope,
)


def test_scope_none_is_not_ready() -> None:
    assert parse_territorial_scope({"territorial_scope": "none"}) is None
    assert build_rfb_readiness({"territorial_scope": "none"})["scopeReady"] is False
    try:
        assert_territorial_scope_ready({"territorial_scope": "none"})
    except ForbiddenError:
        return
    raise AssertionError("expected ForbiddenError")


def test_scope_ufs_ready() -> None:
    scope = parse_territorial_scope({"territorial_scope": {"ufs": ["rj", "SP"]}})
    assert scope is not None
    assert scope.ufs == frozenset({"RJ", "SP"})
    readiness = build_rfb_readiness({"territorial_scope": {"ufs": ["RJ"]}})
    assert readiness["scopeReady"] is True
    assert readiness["ingestAllowed"] is False
    assert readiness["nationalLoadAllowed"] is False
    assert readiness["createsTaxCredit"] is False


def test_resume_cursor_roundtrip() -> None:
    cursor = next_resume_plan()
    assert cursor.file_name == "Estabelecimentos0.zip"
    assert cursor.byte_offset == 0
    encoded = ResumeCursor(file_name="Estabelecimentos3.zip", byte_offset=99).encode()
    decoded = ResumeCursor.decode(encoded)
    assert decoded is not None
    planned = next_resume_plan(cursor=decoded)
    assert planned.file_name == "Estabelecimentos3.zip"
    assert planned.byte_offset == 99


def test_ei_policy_excludes_individual_entrepreneur() -> None:
    assert ei_policy_decision(natureza_codigo="2135") == "individual_entrepreneur_excluded"
    assert ei_policy_decision(natureza_codigo=None) == "missing_nature_for_ei_policy"
    assert ei_policy_decision(natureza_codigo="2062") is None


def test_parse_filters_uf_and_excludes_ei() -> None:
    # Full positional Estabelecimentos layout through municipio (index 20).
    body = (
        "11111111;0001;91;1;EMP A;02;;;;;;6201501;;RUA;X;1;;Bairro;20000000;RJ;6001\n"
        "22222222;0001;91;1;EMP B;02;;;;;;6201501;;RUA;X;1;;Bairro;01000000;SP;7107\n"
        "33333333;0001;91;1;EI C;02;;;;;;6201501;;RUA;X;1;;Bairro;20000000;RJ;6001\n"
    ).encode("latin-1")
    scope = parse_territorial_scope({"territorial_scope": {"ufs": ["RJ"]}})
    assert scope is not None
    silver, quarantined, offset = parse_rfb_estabelecimentos(
        body,
        scope=scope,
        nature_by_cnpj_basico={"11111111": "2062", "33333333": "2135"},
        rfb_to_ibge={"6001": "3304557"},
    )
    assert offset > 0
    assert len(silver) == 1
    assert silver[0]["cnpjBasico"] == "11111111"
    assert silver[0]["ibgeCode"] == "3304557"
    assert any(reason == "individual_entrepreneur_excluded" for _, reason in quarantined)
    assert all(row["uf"] == "RJ" for row in silver)


def test_landing_manifest_never_national_or_credit() -> None:
    scope = parse_territorial_scope({"territorial_scope": {"ufs": ["RJ"]}})
    assert scope is not None
    manifest = build_rfb_landing_manifest(
        source_id="RFB-DADOS-ABERTOS",
        official_url="https://dadosabertos.rfb.gov.br/CNPJ/",
        resolved_url="https://dadosabertos.rfb.gov.br/CNPJ/Estabelecimentos0.zip",
        checksum="abc",
        byte_count=10,
        scope=scope,
        resume=ResumeCursor(file_name="Estabelecimentos0.zip", byte_offset=10),
        received_count=2,
        silver_count=1,
        quarantined_count=1,
    )
    assert manifest["nationalLoad"] is False
    assert manifest["createsTaxCredit"] is False
    assert manifest["individualEntrepreneurInGold"] is False
    assert manifest["territorialScope"]["ufs"] == ["RJ"]
