from pathlib import Path


def test_terraform_local_is_documentation_only() -> None:
    text = Path("infra/terraform/environments/local/main.tf").read_text(encoding="utf-8")
    assert "apply is forbidden" in text.lower()
    assert "prevent_destroy" in text
    assert "google" not in text.lower()
    assert "aws_" not in text.lower()
