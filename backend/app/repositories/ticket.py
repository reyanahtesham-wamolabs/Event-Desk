import uuid
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.models.tickets import Ticket
from app.models.enum import TicketTier
from app.utils.exceptions import NotFoundError, ConflictError


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        event_id: str,
        seat_num: int,
        ticket_tier: TicketTier,
        price: int,
        user_id: str | None = None,
    ) -> Ticket:
        ticket = Ticket(
            id=str(uuid.uuid4()),
            event_id=event_id,
            seat_num=seat_num,
            ticket_tier=ticket_tier,
            price=price,
            user_id=None,
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def bulk_create(self, tickets: list[dict]) -> list[Ticket]:
        objs = [
            Ticket(
                id=str(uuid.uuid4()),
                event_id=t["event_id"],
                seat_num=t["seat_num"],
                ticket_tier=t["ticket_tier"],
                price=t["price"],
                user_id=None,
            )
            for t in tickets
        ]
        try:
            self.db.add_all(objs)
            await self.db.commit()
        except Exception as e:
            raise e
        return objs

    async def get(self, ticket_id: str) -> Ticket:
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        return ticket

    async def get_by_event(
        self, event_id: str, tier: TicketTier | None = None
    ) -> Sequence[Ticket]:
        stmt = select(Ticket).where(Ticket.event_id == event_id)
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_available_by_event(
        self, event_id: str, tier: TicketTier | None = None
    ) -> Sequence[Ticket]:
        stmt = select(Ticket).where(
            Ticket.event_id == event_id, Ticket.user_id.is_(None)
        )
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_user(self, user_id: str) -> Sequence[Ticket]:
        stmt = select(Ticket).where(Ticket.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_available(self, event_id: str, tier: TicketTier | None = None) -> int:
        stmt = (
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.event_id == event_id, Ticket.user_id.is_(None))
        )
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def claim_any_available(
        self, event_id: str, tier: TicketTier, user_id: str
    ) -> Ticket:
        try:
            stmt = (
                select(Ticket)
                .where(
                    Ticket.event_id == event_id,
                    Ticket.ticket_tier == tier,
                    Ticket.user_id.is_(None),
                )
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            result = await self.db.execute(stmt)
            ticket = result.scalars().first()

            if ticket is None:
                raise ConflictError(
                    f"No available tickets for event {event_id}, tier {tier}"
                )

            ticket.user_id = user_id
            await self.db.commit()
            await self.db.refresh(ticket)
            return ticket
        except Exception:
            await self.db.rollback()
            raise

    async def claim_specific(self, ticket_id: str, user_id: str) -> Ticket:
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id, Ticket.user_id.is_(None))
            .values(user_id=user_id)
        )
        result = await self.db.execute(stmt)

        if result.rowcount == 0:
            await self.db.rollback()
            if await self.db.get(Ticket, ticket_id) is None:
                raise NotFoundError(f"Ticket {ticket_id} not found")
            raise ConflictError(f"Ticket {ticket_id} already claimed")

        await self.db.commit()
        return await self.get(ticket_id)

    async def release(self, ticket_id: str) -> Ticket:
        """Release a ticket back to available (cancellation)."""
        stmt = update(Ticket).where(Ticket.id == ticket_id).values(user_id=None)
        result = await self.db.execute(stmt)
        if result.rowcount == 0:
            await self.db.rollback()
            raise NotFoundError(f"Ticket {ticket_id} not found")
        await self.db.commit()
        return await self.get(ticket_id)

    async def update(self, ticket_id: str, **fields) -> Ticket:
        ticket = await self.get(ticket_id)
        for key, value in fields.items():
            if not hasattr(ticket, key):
                raise ValueError(f"Invalid field: {key}")
            setattr(ticket, key, value)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def delete(self, ticket_id: str) -> None:
        ticket = await self.db.get(Ticket, ticket_id)
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        await self.db.delete(ticket)
        await self.db.commit()
