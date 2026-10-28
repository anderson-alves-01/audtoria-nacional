"""Validation of a monthly ZIP. The same checks run for downloads and for manual imports."""

from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

MAX_UNCOMPRESSED_BYTES = 12 * 1024**3
MAX_RATIO = 300  # deflate never exceeds about 1000:1; text tables sit far below 300

HTML_MARKERS = (
    b"<!doctype html",
    b"<html",
    b"human verification",
    b"awswafcookiedomainlist",
    b"gokuprops",
    b"<head",
)


@dataclass(frozen=True)
class MemberInfo:
    name: str
    size: int
    compressed: int
    crc: int


@dataclass
class ZipReport:
    ok: bool
    reason: str = ""
    sha256: str = ""
    size: int = 0
    members: list[MemberInfo] = field(default_factory=list)


def looks_like_html(prefix: bytes) -> bool:
    """True for the HTML pages that portals return instead of a file (error, WAF, human check)."""
    head = prefix[:4096].lstrip().lower()
    if head.startswith(b"pk"):
        return False
    return any(marker in head for marker in HTML_MARKERS) or head.startswith(b"<")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_member_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/") or ":" in name:
        return False
    return ".." not in PurePosixPath(name).parts


def validate_zip(path: Path, *, expected_size: int | None = None) -> ZipReport:
    """Structure, signature, CRC and SHA-256. Fails closed with a short reason."""
    if not path.is_file():
        return ZipReport(False, "arquivo_ausente")
    size = path.stat().st_size
    if size == 0:
        return ZipReport(False, "arquivo_vazio", size=0)
    with path.open("rb") as handle:
        prefix = handle.read(4096)
    if looks_like_html(prefix):
        return ZipReport(False, "pagina_html_no_lugar_do_zip", size=size)
    if prefix[:4] != b"PK\x03\x04":
        return ZipReport(False, "assinatura_zip_invalida", size=size)
    if expected_size is not None and expected_size != size:
        return ZipReport(
            False, f"tamanho_diferente_do_esperado({size}!={expected_size})", size=size
        )
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not infos:
                return ZipReport(False, "zip_sem_membros", size=size)
            total = 0
            members: list[MemberInfo] = []
            for info in infos:
                if info.is_dir():
                    continue
                if not safe_member_name(info.filename):
                    return ZipReport(False, f"nome_de_membro_inseguro({info.filename})", size=size)
                total += info.file_size
                if info.compress_size and info.file_size / info.compress_size > MAX_RATIO:
                    return ZipReport(
                        False, f"razao_de_compressao_suspeita({info.filename})", size=size
                    )
                members.append(
                    MemberInfo(info.filename, info.file_size, info.compress_size, info.CRC)
                )
            if total > MAX_UNCOMPRESSED_BYTES:
                return ZipReport(False, "tamanho_descomprimido_acima_do_limite", size=size)
            bad = archive.testzip()
            if bad is not None:
                return ZipReport(False, f"crc_invalido({bad})", size=size)
    except (zipfile.BadZipFile, OSError, NotImplementedError, RuntimeError) as error:
        return ZipReport(False, f"zip_ilegivel({type(error).__name__})", size=size)
    return ZipReport(True, "", sha256_file(path), size, members)
