"""Password and authenticator checks for an operator login. Secrets stay hashed."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time

from sirta_api.domain.errors import UnauthorizedError, ValidationFailedError

SESSION_MODE = "OPERATOR_LOGIN"
_HASH_ROUNDS = 600_000


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValidationFailedError("A senha precisa ter ao menos 12 caracteres.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _HASH_ROUNDS)
    encoded_salt = base64.b64encode(salt).decode("ascii")
    encoded_digest = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${_HASH_ROUNDS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored or not password:
        return False
    parts = stored.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    try:
        rounds = int(parts[1])
        salt = base64.b64decode(parts[2])
        expected = base64.b64decode(parts[3])
    except (ValueError, TypeError):
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(candidate, expected)


def normalize_totp_secret(secret: str) -> str:
    compact = "".join(secret.split()).upper()
    if not compact or len(compact) > 64:
        raise ValidationFailedError("Segredo do autenticador inválido.")
    try:
        base64.b32decode(compact + "=" * ((8 - len(compact) % 8) % 8), casefold=True)
    except Exception as exc:
        raise ValidationFailedError("Segredo do autenticador inválido.") from exc
    return compact


def totp_matches(secret: str, code: str, *, now: float | None = None) -> bool:
    given = str(code or "").strip()
    if len(given) != 6 or not given.isdigit():
        return False
    moment = int(now if now is not None else time.time())
    for shift in (-30, 0, 30):
        if hmac.compare_digest(_totp(secret, moment + shift), given):
            return True
    return False


def confirm_login(
    *,
    active: bool,
    password_hash: str | None,
    totp_secret: str | None,
    password: str,
    code: str,
    now: float | None = None,
) -> bool:
    if not active or not verify_password(password, password_hash):
        raise UnauthorizedError("Acesso não conferiu.")
    if not totp_secret:
        raise UnauthorizedError("Acesso não conferiu.")
    if not totp_matches(totp_secret, code, now=now):
        raise UnauthorizedError("Acesso não conferiu.")
    return True


def _totp(secret: str, moment: int) -> str:
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    counter = int(moment // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % 1_000_000:06d}"
