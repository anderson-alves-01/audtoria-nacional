"""Local worker heartbeat. No fiscal processing in F0."""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime


def main() -> None:
    while True:
        payload = {
            "event": "worker.heartbeat",
            "implementationVersion": "0.3.1",
            "releaseStage": "F0_FOUNDATION",
            "ts": datetime.now(UTC).isoformat(),
        }
        sys.stdout.write(json.dumps(payload) + "\n")
        sys.stdout.flush()
        time.sleep(30)


if __name__ == "__main__":
    main()
