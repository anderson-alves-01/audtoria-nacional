"""Tenant user directory. Mutations stay with the technical administrator."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import AccessPurpose, Territory, User, UserTerritory
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, NotVisibleError, ValidationFailedError
from sirta_api.domain.identities import Role
from sirta_api.domain.users_admin import ROLE_LABELS, keeps_last_technical_admin, user_draft


def list_user_directory(session: Session, *, context: AccessContext) -> dict:
    _ensure_reader(context)
    territories = _territories(session, context)
    purposes = session.scalars(
        select(AccessPurpose).where(AccessPurpose.tenant_id == context.tenant_id)
    ).all()
    users = session.scalars(
        select(User).where(User.tenant_id == context.tenant_id).order_by(User.username)
    ).all()
    record_audit(
        session,
        context=context,
        action="users.list",
        route="/v1/admin/users",
        outcome="success",
        resource_type="user",
    )
    return {
        "createsTaxCredit": False,
        "canManage": _can_manage(context),
        "manageReason": _manage_reason(context),
        "roles": [{"code": code, "label": label} for code, label in ROLE_LABELS.items()],
        "territories": [
            {"id": str(row.id), "code": row.code, "name": row.name} for row in territories
        ],
        "purposes": [
            {"id": str(row.id), "code": row.code, "description": row.description}
            for row in purposes
        ],
        "users": [_public_user(row) for row in users],
    }


def create_user(session: Session, *, context: AccessContext, payload: dict) -> dict:
    context.ensure_can_manage_users()
    draft = user_draft(payload, allowed_territories=_allowed(session, context))
    existing = session.scalar(
        select(User).where(
            User.tenant_id == context.tenant_id,
            User.username == draft["username"],
        )
    )
    if existing is not None:
        raise ValidationFailedError("Já existe um usuário com esse nome neste tenant.")
    user = User(
        id=uuid4(),
        tenant_id=context.tenant_id,
        subject=str(uuid4()),
        username=draft["username"],
        role=draft["role"],
        active=draft["active"],
    )
    session.add(user)
    session.flush()
    _replace_territories(session, user, draft["territoryIds"])
    record_audit(
        session,
        context=context,
        action="users.created",
        route="/v1/admin/users",
        outcome="success",
        resource_type="user",
        resource_id=user.id,
    )
    session.flush()
    return _public_user(user)


def update_user(session: Session, *, context: AccessContext, user_id, payload: dict) -> dict:
    context.ensure_can_manage_users()
    user = _visible_user(session, context, user_id)
    draft = user_draft(payload, allowed_territories=_allowed(session, context))
    keeps_last_technical_admin(
        is_last=_is_last_admin(session, context, user),
        next_role=draft["role"],
        active=draft["active"],
    )
    if user.id == context.user_id and not draft["active"]:
        raise ValidationFailedError("O administrador da sessão não pode encerrar o próprio acesso.")
    duplicate = session.scalar(
        select(User).where(
            User.tenant_id == context.tenant_id,
            User.username == draft["username"],
            User.id != user.id,
        )
    )
    if duplicate is not None:
        raise ValidationFailedError("Já existe um usuário com esse nome neste tenant.")
    user.username = draft["username"]
    user.role = draft["role"]
    user.active = draft["active"]
    _replace_territories(session, user, draft["territoryIds"])
    record_audit(
        session,
        context=context,
        action="users.updated",
        route=f"/v1/admin/users/{user.id}",
        outcome="success",
        resource_type="user",
        resource_id=user.id,
    )
    session.flush()
    return _public_user(user)


def deactivate_user(session: Session, *, context: AccessContext, user_id) -> dict:
    context.ensure_can_manage_users()
    user = _visible_user(session, context, user_id)
    if user.id == context.user_id:
        raise ValidationFailedError("O administrador da sessão não pode encerrar o próprio acesso.")
    keeps_last_technical_admin(
        is_last=_is_last_admin(session, context, user),
        next_role=user.role,
        active=False,
    )
    user.active = False
    record_audit(
        session,
        context=context,
        action="users.deactivated",
        route=f"/v1/admin/users/{user.id}",
        outcome="success",
        resource_type="user",
        resource_id=user.id,
    )
    session.flush()
    return _public_user(user)


def _ensure_reader(context: AccessContext) -> None:
    if context.role == Role.TECH_ADMIN:
        return
    context.ensure_fiscal_read()


def _can_manage(context: AccessContext) -> bool:
    try:
        context.ensure_can_manage_users()
    except ForbiddenError:
        return False
    return True


def _manage_reason(context: AccessContext) -> str | None:
    try:
        context.ensure_can_manage_users()
    except ForbiddenError as exc:
        return str(exc)
    return None


def _territories(session: Session, context: AccessContext) -> list[Territory]:
    return list(
        session.scalars(
            select(Territory)
            .where(Territory.tenant_id == context.tenant_id)
            .order_by(Territory.name)
        ).all()
    )


def _allowed(session: Session, context: AccessContext) -> set:
    return {row.id for row in _territories(session, context)}


def _visible_user(session: Session, context: AccessContext, user_id) -> User:
    user = session.get(User, user_id)
    if user is None or user.tenant_id != context.tenant_id:
        raise NotVisibleError("Usuário não encontrado.")
    return user


def _is_last_admin(session: Session, context: AccessContext, user: User) -> bool:
    if user.role != Role.TECH_ADMIN.value or not user.active:
        return False
    admins = session.scalars(
        select(User).where(
            User.tenant_id == context.tenant_id,
            User.role == Role.TECH_ADMIN.value,
            User.active.is_(True),
        )
    ).all()
    return len(admins) == 1 and admins[0].id == user.id


def _replace_territories(session: Session, user: User, territory_ids: list) -> None:
    current = session.scalars(
        select(UserTerritory).where(UserTerritory.user_id == user.id)
    ).all()
    for row in current:
        session.delete(row)
    session.flush()
    for territory_id in territory_ids:
        session.add(UserTerritory(user_id=user.id, territory_id=territory_id))
    session.flush()
    session.refresh(user)


def _public_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "username": user.username,
        "role": user.role,
        "roleLabel": ROLE_LABELS.get(user.role, user.role),
        "active": user.active,
        "territoryIds": [str(item.id) for item in user.territories],
        "createsTaxCredit": False,
    }
