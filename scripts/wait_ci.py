import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

HEADERS = {
    "User-Agent": "sirta-ci",
    "Accept": "application/vnd.github+json",
}
REPO = "anderson-alves-01/audtoria-nacional"


def _git_token() -> str | None:
    completed = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        check=False,
    )
    for line in completed.stdout.splitlines():
        if line.startswith("password="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return None


def get(url: str) -> dict:
    headers = dict(HEADERS)
    token = _git_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in {403, 429} and attempt < 5:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("github api retries exhausted")


def main() -> int:
    sha_prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    if len(sha_prefix) < 7:
        raise SystemExit("usage: python scripts/wait_ci.py <sha-prefix>")
    deadline = time.time() + 900
    while time.time() < deadline:
        data = get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=15")
        runs = [
            item
            for item in data.get("workflow_runs", [])
            if item["head_sha"].startswith(sha_prefix)
        ]
        if not runs:
            print("waiting for run...")
            time.sleep(20)
            continue
        run = runs[0]
        print(run["id"], run["status"], run.get("conclusion"), run["html_url"])
        if run["status"] == "completed":
            jobs = get(
                f"https://api.github.com/repos/{REPO}/actions/runs/{run['id']}/jobs"
            )["jobs"]
            for job in jobs:
                print("JOB", job["name"], job["conclusion"])
            print("CONCLUSION", run.get("conclusion"))
            return 0 if run.get("conclusion") == "success" else 1
        time.sleep(20)
    print("timeout waiting CI")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
