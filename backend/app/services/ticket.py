from app.models.enum import TicketTier
from app.repositories.ticket import TicketRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserRole
from app.utils.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.repositories.event import EventRepository


class TicketService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session
        self.repo = TicketRepository(db_session)

    async def create_ticket(
        self,
        *,
        user,
        event_id: str,
        seat_num: int,
        ticket_tier: TicketTier,
        price: int,
    ):
        event = await EventRepository.get_event_by_id(self.session,event_id)
        if event.organizer_id == user.id or user.role == UserRole.ADMIN:
            return await self.repo.create(
                event_id=event_id,
                seat_num=seat_num,
                ticket_tier=ticket_tier,
                price=price,
            )
        else:
            raise PermissionDeniedError()

    async def create_tickets_bulk(
        self, user, event, ticket_count: int, tier: TicketTier, ticket_price: int
    ):
        if user.id != event.organizer_id and user.role != UserRole.ADMIN:
            raise PermissionDeniedError()
        ticket_list = []
        for i in range(ticket_count):
            ticket_list.append(
                {
                    "event_id": event.id,
                    "seat_num": i,
                    "ticket_tier": tier,
                    "price": ticket_price,
                }
            )
        return await self.repo.bulk_create(ticket_list)

    async def get_ticket(self, ticket_id: str):
        return await self.repo.get(ticket_id)

    async def list_event_tickets(self, event_id: str, tier: TicketTier | None = None):
        return await self.repo.get_by_event(event_id, tier=tier)

    async def list_available_tickets(
        self, event_id: str, tier: TicketTier | None = None
    ):
        return await self.repo.get_available_by_event(event_id, tier=tier)

    async def list_user_tickets(self, user_id: str):
        return await self.repo.get_by_user(user_id)

    async def available_count(
        self, event_id: str, tier: TicketTier | None = None
    ) -> int:
        return await self.repo.count_available(event_id, tier=tier)

    async def purchase_any_available(
        self, event_id: str, tier: TicketTier, user_id: str
    ):
        return await self.repo.claim_any_available(event_id, tier, user_id)

    async def purchase_specific_seat(self, ticket_id: str, user_id: str):
        return await self.repo.claim_specific(ticket_id, user_id)

    async def cancel_ticket(self, ticket_id: str, user_id: str):
        return await self.repo.release(ticket_id, owned_by=user_id)

    async def release_all_by_event(self, event_id: str, commit: bool = True) -> int:
        return await self.repo.release_all_by_event(event_id, commit=commit)

    async def update_ticket(self, user, ticket_id: str, **fields):
        ticket = self.repo.get(ticket_id)
        if ticket.user_id == user.id or user.role == UserRole.ADMIN:
            return await self.repo.update(ticket_id, **fields)
        else:
            PermissionDeniedError("You cannot update this ticket")

    async def delete_ticket(self, user, ticket_id: str):
        ticket = await self.repo.get(ticket_id)
        if ticket.user_id == user.id or user.role == UserRole.ADMIN:
            return await self.repo.delete(ticket_id)
        else:
            PermissionDeniedError("You cannot update this ticket")
