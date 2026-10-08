"""Fill the technical administrator secret once. Existing hashes stay."""

from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import User
from sirta_api.adapters.db.session import get_session_factory
from sirta_api.adapters.db.synthetic_ids import USER_ADMIN_ALPHA
from sirta_api.config import Settings, get_settings
from sirta_api.domain.local_login import hash_password, normalize_totp_secret


def apply_admin_credentials(session: Session, settings: Settings) -> bool:
    if not settings.admin_password and not settings.admin_totp_secret:
        return False
    user = session.get(User, USER_ADMIN_ALPHA)
    if user is None:
        return False
    changed = False
    if settings.admin_password and not user.password_hash:
        user.password_hash = hash_password(settings.admin_password)
        changed = True
    if settings.admin_totp_secret and not user.totp_secret:
        user.totp_secret = normalize_totp_secret(settings.admin_totp_secret)
        changed = True
    return changed


def main() -> None:
    session = get_session_factory()()
    try:
        changed = apply_admin_credentials(session, get_settings())
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    print(f"ADMIN_BOOTSTRAP changed={str(changed).lower()}")


if __name__ == "__main__":
    main()
