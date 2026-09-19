import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("SIRTA_LIVE_OFFICIAL") != "1",
    reason="Live official ingest is opt-in and is not part of CI",
)


def test_live_marker_is_opt_in() -> None:
    assert os.environ.get("SIRTA_LIVE_OFFICIAL") == "1"
