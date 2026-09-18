from pathlib import Path

from sirta_api.domain.errors import ForbiddenError


def flags_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "feature-flags.yaml"
        if candidate.exists():
            return candidate
    return Path("config/feature-flags.yaml")


GATES = (
    {"id": "G0", "component": "municipal_program", "status": "BLOCKED"},
    {"id": "G1", "component": "diagnosis", "status": "BLOCKED"},
    {"id": "G4", "component": "iss_specialist", "status": "BLOCKED"},
    {
        "id": "G6",
        "component": "finance",
        "localStatus": "LOCAL_GO",
        "officialStatus": "OFFICIAL_BLOCKED",
    },
    {
        "id": "G7",
        "component": "transfers",
        "localStatus": "LOCAL_GO",
        "officialStatus": "OFFICIAL_BLOCKED",
    },
    {
        "id": "G8",
        "component": "ibs_cbs",
        "localStatus": "LOCAL_GO",
        "officialStatus": "OFFICIAL_BLOCKED",
        "binding": False,
        "operational": False,
        "homologated": False,
    },
    {"id": "G9", "component": "pilot", "status": "BLOCKED"},
    {"id": "G10", "component": "production", "status": "BLOCKED"},
)


def load_flags() -> dict[str, bool]:
    flags: dict[str, bool] = {}
    for raw in flags_path().read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        flags[key.strip()] = value.strip().lower() == "true"
    return flags


def assert_flag_disabled(name: str) -> None:
    if load_flags().get(name, True):
        raise ForbiddenError(f"Feature flag {name} is not authorized")


def program_snapshot() -> dict:
    return {
        "flags": load_flags(),
        "gates": [dict(item) for item in GATES],
        "humanApprovalFabricated": False,
    }
