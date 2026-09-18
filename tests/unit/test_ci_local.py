from pathlib import Path


def test_ci_has_no_cloud_credentials() -> None:
    text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "gcp_" not in lowered
    assert "aws_access" not in lowered
    assert "tf_token" not in lowered
    assert "googleapis" not in lowered
    assert 'node-version: "20.19.0"' in text
    assert 'python-version: "3.12"' in text
    assert text.index("- name: Migrate") < text.index("- name: Tests")
