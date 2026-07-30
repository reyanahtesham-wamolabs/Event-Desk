from fastapi import Depends
from app.dependencies.db import get_db
from app.services.auth import UserAuthenticationServices
from app.services.event import EventService
from app.services.tag import TagService
from app.services.ticket import TicketService
from app.services.review import ReviewService
def get_auth_service(db=Depends(get_db)) -> UserAuthenticationServices:
    return UserAuthenticationServices(db_session=db)

def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(db_session=db)

def get_tag_service(db=Depends(get_db)) -> TagService:
    return TagService(db_session=db)

def get_ticket_service(db = Depends(get_db)) -> TicketService:
    return TicketService(db_session=db)

def get_review_service(db=Depends(get_db)) -> ReviewService:
    return ReviewService(db_session=db)
