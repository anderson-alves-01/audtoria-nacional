from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.application.public_open_session import mint_public_open_session
from sirta_api.config import get_settings

router = APIRouter(tags=["auth"])


@router.get("/v1/auth/public-open-session")
def get_public_open_session(session: Session = Depends(get_session)) -> dict:
    return mint_public_open_session(session, settings=get_settings())
