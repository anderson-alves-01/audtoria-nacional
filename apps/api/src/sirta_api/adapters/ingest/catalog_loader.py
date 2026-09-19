from pathlib import Path

import yaml

CATALOG_RELATIVE = Path("contracts/sources/official-catalog.yaml")


def catalog_path() -> Path:
    here = Path(__file__).resolve()
    for parent in [Path.cwd(), *here.parents]:
        candidate = parent / CATALOG_RELATIVE
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("official source catalog is missing")


def load_official_catalog() -> dict:
    payload = yaml.safe_load(catalog_path().read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload.get("sources"):
        raise ValueError("official source catalog is invalid")
    return payload


def catalog_sources() -> list[dict]:
    return list(load_official_catalog()["sources"])


def catalog_source(source_id: str) -> dict | None:
    for item in catalog_sources():
        if item.get("source_id") == source_id:
            return item
    return None
