from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "sped_source_verify", ROOT / "tools" / "ops" / "sped-source-verify.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_read_manifest_parses_file_bytes_and_sha(tmp_path: Path) -> None:
    mod = _load()
    manifest = tmp_path / "m.txt"
    sha = "a" * 64
    manifest.write_text(
        f"started=x\nhist: titulo\n  url=https://x\n  file=docs/a.ods\n  bytes=3 sha256={sha}\n",
        encoding="utf-8",
    )
    assert mod.read_manifest(manifest) == [("docs/a.ods", 3, sha)]


def test_verify_accepts_matching_file_and_flags_every_kind_of_change(tmp_path: Path) -> None:
    mod = _load()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.ods").write_bytes(b"abc")
    good = [("docs/a.ods", 3, _sha(b"abc"))]
    assert mod.verify(good, tmp_path) == []

    assert any("SHA256" in p for p in mod.verify([("docs/a.ods", 3, _sha(b"xyz"))], tmp_path))
    assert any("TAMANHO" in p for p in mod.verify([("docs/a.ods", 4, _sha(b"abc"))], tmp_path))
    assert any("AUSENTE" in p for p in mod.verify([("docs/b.ods", 3, _sha(b"abc"))], tmp_path))
    assert mod.verify([], tmp_path) == ["manifesto sem entradas"]


def test_recorded_manifest_lists_both_official_originals() -> None:
    mod = _load()
    entries = mod.read_manifest(mod.MANIFEST)
    names = {entry[0].rsplit("/", 1)[-1] for entry in entries}
    assert names == {
        "Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods",
        "Estat_NFe_CFOP_2025_v1_formatada.ods",
    }
