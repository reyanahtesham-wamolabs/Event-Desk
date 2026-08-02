from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db

from app.dependencies.authorization import get_current_user, require_permission
from app.models.event import EventCategory, EventStatus
from app.models.enum import TicketTier
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.permissions import Permission
from app.services.event import EventService
from app.services.ticket import TicketService
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.ticket import (
    TicketCreate,
    TicketBulkCreate,
    TicketResponse,
    PurchaseAnyRequest,
    AvailableCountResponse,
)
from app.schemas.review import ReviewCreate, ReviewResponse as ReviewResponse
from app.services.review import ReviewService
from app.dependencies.services import get_event_service, get_ticket_service, get_review_service
from app.utils.exceptions import NotFoundError, ConflictError, ValidationError
from app.models.notification import NotificationType
from app.core.scheduler import schedule_notification, schedule_bulk_notifications

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    payload: EventCreate,
    user: User = Depends(require_permission(Permission.CREATE_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.create_event(user, **payload.model_dump())


@router.get("", response_model=list[EventResponse])
async def list_published_events(
    category: EventCategory | None = None,
    tag_name: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(require_permission(Permission.VIEW_PUBLISHED_EVENTS)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.list_published_events(
        category=category, tag_name=tag_name, skip=skip, limit=limit
    )


@router.get("/mine", response_model=list[EventResponse])
async def list_my_events(
    status: EventStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.list_my_events(
        user, status=status, skip=skip, limit=limit
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    user: User = Depends(get_current_user),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.get_event(event_id,user)


@router.patch("/{event_id}", response_model=EventResponse)
async def edit_event(
    event_id: str,
    payload: EventUpdate,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    fields = payload.model_dump(exclude_unset=True)
    return await events_service.edit_event(user, event_id, **fields)


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    return await events_service.publish_event(user, event_id)


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.CANCEL_EVENT)),
    events_service: EventService = Depends(get_event_service),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    event = await events_service.cancel_event(user, event_id)
    # Notify all ticket holders in the background
    booked_tickets = await ticket_service.list_event_tickets(event_id)
    holder_ids = {t.user_id for t in booked_tickets if t.user_id is not None}
    if holder_ids:
        notifications = [
            {
                "user_id": uid,
                "type": NotificationType.EVENT_CANCELLED,
                "message": f"The event '{event.title}' has been cancelled.",
                "event_id": event_id,
            }
            for uid in holder_ids
        ]
        schedule_bulk_notifications(notifications)
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    user: User = Depends(require_permission(Permission.DELETE_EVENT)),
    events_service: EventService = Depends(get_event_service),
):
    await events_service.delete_event(user, event_id)



@router.post("/{event_id}/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    event_id: str,
    payload: TicketCreate,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    
    return await ticket_service.create_ticket(
        user=user,
        event_id=event_id,
        seat_num=payload.seat_num,
        ticket_tier=payload.ticket_tier,
        price=payload.price,
    )


@router.post("/{event_id}/tickets/bulk", response_model=list[TicketResponse], status_code=201)
async def create_tickets_bulk(
    event_id: str,
    payload: TicketBulkCreate,
    user: User = Depends(require_permission(Permission.EDIT_EVENT)),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    tickets = []
    for t in payload.tickets:
        ticket = await ticket_service.create_ticket(
            user=user,
            event_id=event_id,
            seat_num=t.seat_num,
            ticket_tier=t.ticket_tier,
            price=t.price,
        )
        tickets.append(ticket)
    return tickets


@router.get("/{event_id}/tickets", response_model=list[TicketResponse])
async def list_event_tickets(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_event_tickets(event_id, tier=tier)


@router.get("/{event_id}/tickets/available", response_model=list[TicketResponse])
async def list_available_tickets(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_available_tickets(event_id, tier=tier)


@router.get("/{event_id}/tickets/available/count", response_model=AvailableCountResponse)
async def available_count(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    count = await ticket_service.available_count(event_id, tier=tier)
    return AvailableCountResponse(event_id=event_id, tier=tier, available=count)


@router.post("/{event_id}/purchase-any", response_model=TicketResponse)
async def purchase_any_available(
    event_id: str,
    payload: PurchaseAnyRequest,
    user: User = Depends(require_permission(Permission.BOOK_TICKET)),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        ticket = await ticket_service.purchase_any_available(event_id, payload.tier, user.id)
        schedule_notification(
            user_id=user.id,
            notification_type=NotificationType.TICKET_CONFIRMATION,
            message=f"Your booking for ticket {ticket.id} has been confirmed.",
            event_id=event_id,
        )
        return ticket
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ConflictError as e:
        raise HTTPException(409, str(e))


@router.post("/{event_id}/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    event_id: str,
    payload: ReviewCreate,
    user: User = Depends(require_permission(Permission.LEAVE_REVIEW)),
    review_service: ReviewService = Depends(get_review_service),
    events_service: EventService = Depends(get_event_service),
    db: AsyncSession = Depends(get_db),
):
    try:
        review = await review_service.create_review(
            user, event_id, payload.review, payload.rating
        )
        # Notify event organizer about the new review
        event = await events_service.get_event(event_id, user)
        if event.organizer_id and event.organizer_id != user.id:
            schedule_notification(
                user_id=event.organizer_id,
                notification_type=NotificationType.EVENT_UPDATE,
                message=f"Your event '{event.title}' received a new review.",
                event_id=event_id,
            )
            
        # Extract mentions and notify users
        mentioned_names = list(set(re.findall(r"@(\w+)", payload.review)))
        if mentioned_names:
            user_repo = UserRepository(db)
            mentioned_users = await user_repo.get_users_by_names(mentioned_names)
            mentioned_ids = {u.id for u in mentioned_users if u.id != user.id}
            
            if mentioned_ids:
                mentions = [
                    {
                        "user_id": uid,
                        "type": NotificationType.REVIEW_MENTION,
                        "message": f"{user.name} mentioned you in a review for '{event.title}'.",
                        "event_id": event_id,
                    }
                    for uid in mentioned_ids
                ]
                schedule_bulk_notifications(mentions)
                
        return review
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ValidationError as e:
        raise HTTPException(422, str(e))


@router.get("/{event_id}/reviews", response_model=list[ReviewResponse])
async def list_event_reviews(
    event_id: str,
    user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.list_event_reviews(event_id)
