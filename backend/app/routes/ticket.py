from fastapi import APIRouter, Depends, HTTPException
from app.models.enum import TicketTier
from app.services.ticket import TicketService
from app.schemas.ticket import (
    TicketResponse,
    TicketUpdate,
)
from app.core.permissions import Permission
from app.dependencies.authorization import get_current_user,require_permission
from app.models.user import User
from app.dependencies.services import get_ticket_service
from app.utils.exceptions import NotFoundError, ConflictError

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/my-tickets", response_model=list[TicketResponse])
async def list_user_tickets(
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    return await ticket_service.list_user_tickets(user.id)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    user: User = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        return await ticket_service.get_ticket(ticket_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.post("/{ticket_id}/purchase", response_model=TicketResponse)
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


@router.post("/{ticket_id}/cancel", response_model=TicketResponse)
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


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    user: User = Depends(require_permission(Permission.CANCEL_EVENT)),
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
    user: User = Depends(require_permission(Permission.CANCEL_EVENT)),
    ticket_service: TicketService = Depends(get_ticket_service),
):
    try:
        await ticket_service.delete_ticket(ticket_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
