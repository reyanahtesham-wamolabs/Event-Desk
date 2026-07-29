import uuid
from typing import Sequence

from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.models.tickets import Ticket
from app.models.enum import TicketTier
from app.utils.exceptions import NotFoundError,ConflictError


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db


    def create(
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
            user_id=user_id,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def bulk_create(self, tickets: list[dict]) -> list[Ticket]:
        """Bulk-insert tickets when setting up an event's inventory."""
        objs = [
            Ticket(
                id=str(uuid.uuid4()),
                event_id=t["event_id"],
                seat_num=t["seat_num"],
                ticket_tier=t["ticket_tier"],
                price=t["price"],
                user_id=t.get("user_id"),
            )
            for t in tickets
        ]
        self.db.add_all(objs)
        self.db.commit()
        return objs


    def get(self, ticket_id: str) -> Ticket:
        ticket = self.db.get(Ticket, ticket_id)
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        return ticket

    def get_by_event(self, event_id: str, tier: TicketTier | None = None) -> Sequence[Ticket]:
        stmt = select(Ticket).where(Ticket.event_id == event_id)
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        return self.db.execute(stmt).scalars().all()

    def get_available_by_event(
        self, event_id: str, tier: TicketTier | None = None
    ) -> Sequence[Ticket]:
        stmt = select(Ticket).where(
            Ticket.event_id == event_id, Ticket.user_id.is_(None)
        )
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        return self.db.execute(stmt).scalars().all()

    def get_by_user(self, user_id: str) -> Sequence[Ticket]:
        stmt = select(Ticket).where(Ticket.user_id == user_id)
        return self.db.execute(stmt).scalars().all()

    def count_available(self, event_id: str, tier: TicketTier | None = None) -> int:
        stmt = select(func.count()).select_from(Ticket).where(
            Ticket.event_id == event_id, Ticket.user_id.is_(None)
        )
        if tier is not None:
            stmt = stmt.where(Ticket.ticket_tier == tier)
        return self.db.execute(stmt).scalar_one()

    # ---------- CONCURRENCY-SAFE CLAIM OPERATIONS ----------

    def claim_any_available(
        self, event_id: str, tier: TicketTier, user_id: str
    ) -> Ticket:
        """
        Atomically grab ONE available seat of the given tier for this event.
        Uses SELECT ... FOR UPDATE SKIP LOCKED so concurrent requests each
        lock a different row instead of queuing behind each other.

        Caller must not already be inside a transaction that they intend
        to hold open indefinitely — commit/rollback happens here.
        """
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
            ticket = self.db.execute(stmt).scalars().first()

            if ticket is None:
                raise ConflictError(
                    f"No available tickets for event {event_id}, tier {tier}"
                )

            ticket.user_id = user_id
            self.db.commit()
            self.db.refresh(ticket)
            return ticket
        except Exception:
            self.db.rollback()
            raise

    def claim_specific(self, ticket_id: str, user_id: str) -> Ticket:
        """
        Atomically claim a SPECIFIC seat (e.g. user picked seat #14).
        Uses a conditional UPDATE so the DB does the compare-and-swap —
        if two requests race for the same seat, only one row is affected.
        """
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id, Ticket.user_id.is_(None))
            .values(user_id=user_id)
        )
        result = self.db.execute(stmt)

        if result.rowcount == 0:
            self.db.rollback()
            # Distinguish "doesn't exist" from "already taken"
            if self.db.get(Ticket, ticket_id) is None:
                raise NotFoundError(f"Ticket {ticket_id} not found")
            raise ConflictError(f"Ticket {ticket_id} already claimed")

        self.db.commit()
        return self.get(ticket_id)

    def release(self, ticket_id: str) -> Ticket:
        """Release a ticket back to available (cancellation, expired hold, etc.)."""
        stmt = (
            update(Ticket)
            .where(Ticket.id == ticket_id)
            .values(user_id=None)
        )
        result = self.db.execute(stmt)
        if result.rowcount == 0:
            self.db.rollback()
            raise NotFoundError(f"Ticket {ticket_id} not found")
        self.db.commit()
        return self.get(ticket_id)


    def update(self, ticket_id: str, **fields) -> Ticket:
        ticket = self.get(ticket_id)
        for key, value in fields.items():
            if not hasattr(ticket, key):
                raise ValueError(f"Invalid field: {key}")
            setattr(ticket, key, value)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket


    def delete(self, ticket_id: str) -> None:
        ticket = self.db.get(Ticket, ticket_id)
        if not ticket:
            raise NotFoundError(f"Ticket {ticket_id} not found")
        self.db.delete(ticket)
        self.db.commit()