from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.enum import TicketTier
from app.services.ticket import TicketService
from app.schemas.ticket import (
    TicketBulkCreate,
    TicketCreate,
    TicketOut,
    TicketUpdate,
    PurchaseAnyRequest,
    AvailableCountOut,
)
from app.dependencies.authorization import get_current_user
from app.models.user import User
from app.dependencies.services import get_ticket_service
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=201)
async def create_ticket(
    payload: TicketCreate,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.create_ticket(
        event_id=payload.event_id,
        seat_num=payload.seat_num,
        ticket_tier=payload.ticket_tier,
        price=payload.price,
    )


@router.post("/bulk", response_model=list[TicketOut], status_code=201)
async def create_tickets_bulk(
    payload: TicketBulkCreate,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    tickets = []
    for t in payload.tickets:
        ticket = await ticket_service.create_ticket(
            event_id=t.event_id,
            seat_num=t.seat_num,
            ticket_tier=t.ticket_tier,
            price=t.price,
        )
        tickets.append(ticket)
    return tickets


@router.get("/my-tickets", response_model=list[TicketOut])
async def list_user_tickets(
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_user_tickets(user.id)


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: str,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        return await ticket_service.get_ticket(ticket_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/event/{event_id}", response_model=list[TicketOut])
async def list_event_tickets(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_event_tickets(event_id, tier=tier)


@router.get("/event/{event_id}/available", response_model=list[TicketOut])
async def list_available_tickets(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_available_tickets(event_id, tier=tier)


@router.get("/event/{event_id}/available/count", response_model=AvailableCountOut)
async def available_count(
    event_id: str,
    tier: TicketTier | None = Query(default=None),
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    count = await ticket_service.available_count(event_id, tier=tier)
    return AvailableCountOut(event_id=event_id, tier=tier, available=count)


@router.post("/{ticket_id}/purchase", response_model=TicketOut)
async def purchase_specific_seat(
    ticket_id: str,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        return await ticket_service.purchase_specific_seat(ticket_id, user.id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ConflictError as e:
        raise HTTPException(409, str(e))


@router.post("/event/{event_id}/purchase-any", response_model=TicketOut)
async def purchase_any_available(
    event_id: str,
    payload: PurchaseAnyRequest,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        return await ticket_service.purchase_any_available(event_id, payload.tier, user.id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ConflictError as e:
        raise HTTPException(409, str(e))


@router.post("/{ticket_id}/cancel", response_model=TicketOut)
async def cancel_ticket(
    ticket_id: str,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        return await ticket_service.cancel_ticket(ticket_id, user.id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except ConflictError as e:
        raise HTTPException(403, str(e))


@router.patch("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        fields = payload.model_dump(exclude_unset=True)
        return await ticket_service.update_ticket(ticket_id, **fields)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(
    ticket_id: str,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        await ticket_service.delete_ticket(ticket_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
