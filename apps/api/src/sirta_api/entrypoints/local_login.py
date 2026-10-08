from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.application.local_login import login_operator
from sirta_api.config import get_settings

router = APIRouter(tags=["auth"])


@router.post("/v1/auth/login")
def post_login(payload: dict, session: Session = Depends(get_session)) -> dict:
    return login_operator(session, settings=get_settings(), payload=payload)
