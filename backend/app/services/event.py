from datetime import datetime, timezone
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.models.event import Event, EventCategory, EventStatus
from app.models.user import UserRole as Role, User
from app.repositories.event import EventRepository as events_repo
from app.repositories.tag import TagRepository as tags_repo

# Statuses an event can never move out of via normal edits
TERMINAL_STATUSES = {EventStatus.CANCELLED, EventStatus.COMPLETED}

class EventService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session

    def _get_session(self, session=None) -> AsyncSession:
        sess = session or self.session
        if sess is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session missing",
            )
        return sess

    def _event_owner(self, user: User, event: Event) -> None:
        if user.role==Role.ADMIN:
            return 
        if event.organizer_id != user.id:
            raise AuthorizationError("You do not have access to this event")

    def _validate_event_time(self, event_time: datetime) -> None:
        if event_time <= datetime.now(timezone.utc):
            raise ValidationError("Event time must be in the future")

    def _validate_total_tickets(self, total_tickets: int) -> None:
        if total_tickets <= 0:
            raise ValidationError("Total tickets must be greater than zero")

    async def _validate_tag_ids(self, tag_ids: list[str], session=None) -> None:
        sess = self._get_session(session)
        for tag_id in tag_ids:
            if await tags_repo.get_tag_by_id(sess, tag_id) is None:
                raise ValidationError(f"Tag '{tag_id}' does not exist")

    async def create_event(
        self,
        current_user: User,
        title: str,
        event_time: datetime,
        total_tickets: int,
        category: EventCategory,
        description: str | None = None,
        tag_ids: list[str] | None = None,
        session=None
    ) -> Event:
        sess = self._get_session(session)
        if not title or not title.strip():
            raise ValidationError("Title is required")

        self._validate_event_time(event_time)
        self._validate_total_tickets(total_tickets)

        if tag_ids:
            await self._validate_tag_ids(tag_ids, session=sess)

        return await events_repo.create_event(
            sess,
            title=title.strip(),
            event_time=event_time,
            total_tickets=total_tickets,
            category=category,
            organizer_id=current_user.id,
            description=description,
            status=EventStatus.DRAFT,
            tag_ids=tag_ids,
        )

    async def get_event(self, event_id: str, session=None) -> Event:
        sess = self._get_session(session)
        event = await events_repo.get_event_by_id(sess, event_id)
        if not event:
            raise NotFoundError(f"Event '{event_id}' not found")
        return event

    async def list_published_events(
        self,
        category: EventCategory | None = None,
        tag_name: str | None = None,
        skip: int = 0,
        limit: int = 20,
        session=None
    ) -> list[Event]:
        """Publicly viewable events — no ownership restriction, any authenticated user can call this."""
        sess = self._get_session(session)
        if skip < 0:
            raise ValidationError("skip must be >= 0")
        if limit <= 0 or limit > 100:
            raise ValidationError("limit must be between 1 and 100")

        return await events_repo.list_events(
            sess,
            status=EventStatus.PUBLISHED,
            category=category,
            tag_name=tag_name,
            skip=skip,
            limit=limit,
        )

    async def list_my_events(
        self,
        current_user: User,
        status: EventStatus | None = None,
        skip: int = 0,
        limit: int = 20,
        session=None
    ) -> list[Event]:
        """Events belonging to the requesting organizer, any status (draft/published/etc)."""
        sess = self._get_session(session)
        return await events_repo.list_events(
            sess,
            organizer_id=current_user.id,
            status=status,
            skip=skip,
            limit=limit,
        )

    async def edit_event(
        self,
        current_user: User,
        event_id: str,
        session=None,
        **fields,
    ) -> Event:
        """
        Partial update of an event. Only the organizer who owns it, or an admin, may edit.
        Cancelled or completed events are immutable.
        """
        sess = self._get_session(session)
        event = await self.get_event(event_id, session=sess)
        self._event_owner(current_user, event)

        if event.status in TERMINAL_STATUSES:
            raise ValidationError(f"Cannot edit an event that is {event.status.value}")

        fields.pop("organizer_id", None)
        fields.pop("status", None)

        if "event_time" in fields and fields["event_time"] is not None:
            self._validate_event_time(fields["event_time"])

        if "total_tickets" in fields and fields["total_tickets"] is not None:
            new_total = fields["total_tickets"]
            self._validate_total_tickets(new_total)
            booked = sum(1 for t in event.tickets if t.status != "cancelled")
            if new_total < booked:
                raise ValidationError(
                    f"Cannot set total_tickets below {booked}, the number already booked"
                )

        if "title" in fields and fields["title"] is not None:
            if not fields["title"].strip():
                raise ValidationError("Title cannot be empty")
            fields["title"] = fields["title"].strip()

        tag_ids = fields.pop("tag_ids", None)
        updated = await events_repo.update_event(sess, event_id, **fields)

        if tag_ids is not None:
            await self._validate_tag_ids(tag_ids, session=sess)
            updated = await events_repo.set_event_tags(sess, event_id, tag_ids)

        return updated

    async def publish_event(self, current_user: User, event_id: str, session=None) -> Event:
        """Move an event from draft to published."""
        sess = self._get_session(session)
        event = await self.get_event(event_id, session=sess)
        self._event_owner(current_user, event)

        if event.status != EventStatus.DRAFT:
            raise ValidationError(f"Cannot publish an event that is {event.status.value}")

        return await events_repo.update_event(sess, event_id, status=EventStatus.PUBLISHED)

    async def cancel_event(self, current_user: User, event_id: str, session=None) -> Event:
        sess = self._get_session(session)
        event = await self.get_event(event_id, session=sess)
        self._event_owner(current_user, event)

        if event.status in TERMINAL_STATUSES:
            raise ValidationError(f"Event is already {event.status.value}")

        updated = await events_repo.update_event(sess, event_id, status=EventStatus.CANCELLED)
        return updated

    async def delete_event(self, current_user: User, event_id: str, session=None) -> None:
        sess = self._get_session(session)
        event = await self.get_event(event_id, session=sess)
        if current_user.role != Role.ADMIN:
            raise AuthorizationError("Only admins may permanently delete events")

        if event.tickets:
            raise ValidationError(
                "Cannot delete an event with existing bookings — cancel it instead"
            )

        await events_repo.delete_event(sess, event_id)