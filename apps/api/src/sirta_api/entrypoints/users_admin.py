"""User and access directory for the current tenant."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.users_admin import (
    create_user,
    deactivate_user,
    list_user_directory,
    update_user,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/admin/users")
def get_users(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_user_directory(session, context=context)


@router.post("/v1/admin/users")
def post_user(
    payload: dict,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return create_user(session, context=context, payload=payload)


@router.put("/v1/admin/users/{userId}")
def put_user(
    userId: UUID,
    payload: dict,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return update_user(session, context=context, user_id=userId, payload=payload)


@router.delete("/v1/admin/users/{userId}")
def delete_user(
    userId: UUID,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return deactivate_user(session, context=context, user_id=userId)
