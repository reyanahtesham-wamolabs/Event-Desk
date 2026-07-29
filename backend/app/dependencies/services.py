from fastapi import Depends
from app.dependencies.db import get_db
from app.services.auth import UserAuthenticationServices


def get_auth_service(db=Depends(get_db)) -> UserAuthenticationServices:
    return UserAuthenticationServices(db_session=db)
