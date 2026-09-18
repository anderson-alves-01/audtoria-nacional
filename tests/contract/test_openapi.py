from pathlib import Path

import yaml
from openapi_spec_validator import validate


def test_active_openapi_spec_is_valid() -> None:
    spec = yaml.safe_load(Path("contracts/openapi/sirta-v1.yaml").read_text(encoding="utf-8"))
    validate(spec)


def test_legacy_outline_is_marked_deprecated() -> None:
    text = Path("contracts/openapi/api-outline.yaml").read_text(encoding="utf-8")
    assert "DEPRECATED" in text
    assert "sirta-v1.yaml" in text
