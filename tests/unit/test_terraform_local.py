from pathlib import Path

ROOT = Path("infra/terraform")
ENVIRONMENTS = ("local", "dev", "staging", "prod")


def test_terraform_tree_has_no_cloud_providers() -> None:
    files = list(ROOT.rglob("*.tf"))
    assert files
    for path in files:
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


def test_environments_use_documentation_module() -> None:
    for name in ENVIRONMENTS:
        path = ROOT / "environments" / name / "main.tf"
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert "apply is forbidden" in lowered
        assert "../../modules/documentation_stack" in text
        assert f'environment = "{name}"' in text
        assert "prevent_destroy" in text or "documentation_stack" in text


def test_no_terraform_var_files_with_secrets() -> None:
    assert list(ROOT.rglob("*.tfvars")) == []
    assert list(ROOT.rglob("*.auto.tfvars")) == []
