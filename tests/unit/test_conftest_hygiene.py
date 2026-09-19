from pathlib import Path


def test_conftest_does_not_drop_all_on_shared_database() -> None:
    text = Path("tests/conftest.py").read_text(encoding="utf-8")
    assert "drop_all" not in text
    assert "command.upgrade" in text
