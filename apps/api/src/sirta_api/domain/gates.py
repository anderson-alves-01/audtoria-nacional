from pathlib import Path

from sirta_api.domain.errors import ForbiddenError


def flags_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "feature-flags.yaml"
        if candidate.exists():
            return candidate
    return Path("config/feature-flags.yaml")


G0_CHECKLIST = (
    {"id": "sponsor", "label": "Patrocinador nomeado", "met": False},
    {"id": "pilot_municipality", "label": "Município piloto definido", "met": False},
    {"id": "dpa", "label": "DPA assinado", "met": False},
    {"id": "governance", "label": "Comitê gestor formalizado", "met": False},
)
G1_CHECKLIST = (
    {"id": "systems_inventory", "label": "Inventário de sistemas homologado", "met": False},
    {"id": "controlled_sample", "label": "Amostra controlada autorizada", "met": False},
    {"id": "lgpd_diagnosis", "label": "Diagnóstico LGPD homologado", "met": False},
    {"id": "no_recovery_promise", "label": "Sem promessa prévia de recuperação", "met": False},
)

GATES = (
    {
        "id": "G0",
        "component": "municipal_program",
        "status": "BLOCKED",
        "checklist": list(G0_CHECKLIST),
    },
    {
        "id": "G1",
        "component": "diagnosis",
        "status": "BLOCKED",
        "checklist": list(G1_CHECKLIST),
    },
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
    gates = []
    for item in GATES:
        copied = dict(item)
        if "checklist" in copied:
            copied["checklist"] = [dict(row) for row in copied["checklist"]]
        gates.append(copied)
    return {
        "flags": load_flags(),
        "gates": gates,
        "humanApprovalFabricated": False,
        "canApprove": False,
    }
