from pathlib import Path


def test_node_20_is_pinned() -> None:
    nvmrc = Path(".nvmrc").read_text(encoding="utf-8").strip()
    assert nvmrc == "20.19.0"
    package = Path("apps/web/package.json").read_text(encoding="utf-8")
    assert '">=20.19.0 <21"' in package
