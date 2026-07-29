import uuid
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tickets import Ticket
from app.models.event import Event, EventStatus
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
        except Exception:
            await self.db.rollback()
            raise
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

    async def count_available(
        self, event_id: str, tier: TicketTier | None = None
    ) -> int:
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
        """
        Atomically claim any available ticket for a *published* event.

        Lock order:
          1. Lock the event row with SELECT … FOR UPDATE.
          2. Verify status is PUBLISHED.
          3. Lock + claim one available ticket with SELECT … FOR UPDATE SKIP LOCKED.

        cancel_event acquires the same event-row lock (via its UPDATE on the event)
        before releasing tickets, so claim and cancel are fully serialised.
        """
        try:
            # Step 1: Lock the event row so cancel_event cannot interleave.
            event_stmt = (
                select(Event)
                .where(Event.id == event_id)
                .with_for_update()
            )
            event_result = await self.db.execute(event_stmt)
            event = event_result.scalar_one_or_none()

            if event is None:
                raise NotFoundError(f"Event '{event_id}' not found")

            # Step 2: Status check — now authoritative because we hold the lock.
            if event.status != EventStatus.PUBLISHED:
                raise ConflictError(
                    f"Tickets can only be purchased for published events "
                    f"(current status: {event.status.value})"
                )

            # Step 3: Claim any unclaimed ticket of the requested tier.
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
                    f"No available {tier.value} tickets for event {event_id}"
                )

            ticket.user_id = user_id
            await self.db.commit()
            await self.db.refresh(ticket)
            return ticket
        except Exception:
            await self.db.rollback()
            raise

    async def claim_specific(self, ticket_id: str, user_id: str) -> Ticket:
        """
        Atomically claim a specific ticket only if it is unclaimed AND its
        event is currently PUBLISHED.

        Lock order:
          1. Lock the event row with SELECT … FOR UPDATE.
          2. Verify status is PUBLISHED.
          3. UPDATE the ticket row WHERE user_id IS NULL.

        This is the same lock order as claim_any_available and cancel_event,
        preventing any interleaving that would leave a booking on a cancelled event.
        """
        try:
            # Step 1: Resolve event_id from the ticket, then lock the event row.
            ticket_lookup = await self.db.get(Ticket, ticket_id)
            if ticket_lookup is None:
                raise NotFoundError(f"Ticket {ticket_id} not found")

            event_stmt = (
                select(Event)
                .where(Event.id == ticket_lookup.event_id)
                .with_for_update()
            )
            event_result = await self.db.execute(event_stmt)
            event = event_result.scalar_one_or_none()

            # Step 2: Status check — authoritative because we hold the lock.
            if event is None or event.status != EventStatus.PUBLISHED:
                status_val = event.status.value if event else "unknown"
                raise ConflictError(
                    f"Tickets can only be purchased for published events "
                    f"(current status: {status_val})"
                )

            # Step 3: Atomically claim the ticket only if still unclaimed.
            stmt = (
                update(Ticket)
                .where(Ticket.id == ticket_id, Ticket.user_id.is_(None))
                .values(user_id=user_id)
            )
            result = await self.db.execute(stmt)

            if result.rowcount == 0:
                raise ConflictError(f"Ticket {ticket_id} is already claimed")

            await self.db.commit()
            return await self.get(ticket_id)
        except Exception:
            await self.db.rollback()
            raise

    async def release(self, ticket_id: str, owned_by: str) -> Ticket:
        """
        Release a ticket back to available, atomically verifying that the
        requesting user still owns it in the WHERE clause — prevents a race
        where another user has since claimed the ticket after an event
        cancellation released it.
        """
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id, Ticket.user_id == owned_by)
            .values(user_id=None)
        )
        result = await self.db.execute(stmt)
        if result.rowcount == 0:
            await self.db.rollback()
            ticket = await self.db.get(Ticket, ticket_id)
            if ticket is None:
                raise NotFoundError(f"Ticket {ticket_id} not found")
            raise ConflictError(
                f"Ticket {ticket_id} does not belong to you or is already released"
            )
        await self.db.commit()
        return await self.get(ticket_id)

    async def release_all_by_event(self, event_id: str, commit: bool = True) -> int:
        """Release all booked tickets for an event back to available. Returns the number of tickets released."""
        stmt = (
            update(Ticket)
            .where(Ticket.event_id == event_id, Ticket.user_id.isnot(None))
            .values(user_id=None)
        )
        result = await self.db.execute(stmt)
        if commit:
            await self.db.commit()
        return result.rowcount

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
