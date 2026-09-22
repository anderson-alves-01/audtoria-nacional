from pathlib import Path

ROOT = Path("infra/terraform")
DOC_ENVIRONMENTS = ("local", "dev", "staging")
PROD_ENV = "prod"


def test_non_prod_environments_have_no_cloud_providers() -> None:
    for name in DOC_ENVIRONMENTS:
        for path in (ROOT / "environments" / name).rglob("*.tf"):
            text = path.read_text(encoding="utf-8").lower()
            assert "hashicorp/google" not in text
            assert "hashicorp/aws" not in text
            assert "hashicorp/azurerm" not in text
            assert "google_" not in text
            assert "aws_" not in text
            assert "azurerm_" not in text


def test_documentation_module_forbids_apply() -> None:
    text = Path("infra/terraform/modules/documentation_stack/main.tf").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "apply is forbidden" in lowered
    assert "prevent_destroy" in text
    assert "hashicorp/null" in text


def test_non_prod_environments_use_documentation_module() -> None:
    for name in DOC_ENVIRONMENTS:
        path = ROOT / "environments" / name / "main.tf"
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "apply is forbidden" in lowered
        assert "../../modules/documentation_stack" in text
        assert f'environment = "{name}"' in text
        assert "prevent_destroy" in text or "documentation_stack" in text


def test_prod_environment_is_g10_gated() -> None:
    text = (ROOT / "environments" / PROD_ENV / "main.tf").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "cloud_apply_authorized" in lowered
    assert "hashicorp/aws" in lowered
    assert "skip_credentials_validation" in lowered
    assert "documentation-only-until-g10" in lowered
    assert "var.cloud_apply_authorized" in text


def test_no_terraform_var_files_with_secrets() -> None:
    assert list(ROOT.rglob("*.tfvars")) == []
    assert list(ROOT.rglob("*.auto.tfvars")) == []
