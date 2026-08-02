from fastapi import Depends
from app.dependencies.db import get_db
from app.services.auth import UserAuthenticationServices
from app.services.event import EventService
from app.services.tag import TagService

def get_auth_service(db=Depends(get_db)) -> UserAuthenticationServices:
    return UserAuthenticationServices(db_session=db)

def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(db_session=db)

def get_tag_service(db=Depends(get_db)) -> TagService:
    return TagService(db_session=db)
