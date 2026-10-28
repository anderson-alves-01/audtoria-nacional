from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_current_state_is_valid_yaml_and_next_action_is_text() -> None:
    state = yaml.safe_load((ROOT / "current-state.yaml").read_text(encoding="utf-8"))
    assert isinstance(state, dict)
    assert isinstance(state["next_action"], str) and state["next_action"]
