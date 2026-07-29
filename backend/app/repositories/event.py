from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.event import Event, EventCategory, EventStatus, Tag


def _event_query():
    """Base query with tags eagerly loaded to avoid N+1s on every read."""
    return select(Event).options(selectinload(Event.tags), selectinload(Event.tickets))


class EventRepository:

    @staticmethod
    async def create_event(
        session: AsyncSession,
        title: str,
        event_time: datetime,
        total_tickets: int,
        category: EventCategory,
        organizer_id: str | None = None,
        description: str | None = None,
        status: EventStatus = EventStatus.DRAFT,
        tag_ids: list[str] | None = None,
    ) -> Event:
        event = Event(
            title=title,
            description=description,
            event_time=event_time,
            total_tickets=total_tickets,
            category=category,
            status=status,
            organizer_id=organizer_id,
        )

        if tag_ids:
            result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
            event.tags = list(result.scalars().all())

        session.add(event)
        await session.commit()
        await session.refresh(event, attribute_names=["tags"])
        return event

    @staticmethod
    async def get_event_by_id(session: AsyncSession, event_id: str) -> Event | None:
        result = await session.execute(_event_query().where(Event.id == event_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_events(
        session: AsyncSession,
        status: EventStatus | None = None,
        category: EventCategory | None = None,
        organizer_id: str | None = None,
        tag_name: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Event]:
        query = _event_query()
        # uncomment when testing frontend
        # if status is not None:
        #     query = query.where(Event.status == status)
        # if category is not None:
        #     query = query.where(Event.category == category)
        if organizer_id is not None:
            query = query.where(Event.organizer_id == organizer_id)
        if tag_name is not None:
            query = query.join(Event.tags).where(Tag.name == tag_name)

        query = query.order_by(Event.event_time).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().unique().all())

    @staticmethod
    async def update_event(
        session: AsyncSession,
        event_id: str,
        **fields,
    ) -> Event | None:
        """
        Partial update. Pass only the fields you want to change, e.g.
        update_event(session, event_id, title="New title", status=EventStatus.PUBLISHED)
        """
        event = await EventRepository.get_event_by_id(session, event_id)
        if not event:
            return None

        for key, value in fields.items():
            if not hasattr(event, key):
                raise ValueError(f"Event has no field '{key}'")
            setattr(event, key, value)

        await session.commit()
        await session.refresh(event, attribute_names=["tags"])
        return event

    @staticmethod
    async def delete_event(session: AsyncSession, event_id: str) -> bool:
        event = await session.get(Event, event_id)
        if not event:
            return False
        await session.delete(event)
        await session.commit()
        return True

    @staticmethod
    async def set_event_tags(
        session: AsyncSession, event_id: str, tag_ids: list[str]
    ) -> Event | None:
        """Replace an event's full tag set."""
        event = await EventRepository.get_event_by_id(session, event_id)
        if not event:
            return None

        result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        event.tags = list(result.scalars().all())

        await session.commit()
        await session.refresh(event, attribute_names=["tags"])
        return event

    @staticmethod
    async def add_tag_to_event(
        session: AsyncSession, event_id: str, tag_id: str
    ) -> Event | None:
        event = await EventRepository.get_event_by_id(session, event_id)
        if not event:
            return None

        tag = await session.get(Tag, tag_id)
        if not tag:
            raise ValueError(f"Tag '{tag_id}' not found")

        if tag not in event.tags:
            event.tags.append(tag)
            await session.commit()
            await session.refresh(event, attribute_names=["tags"])

        return event

    @staticmethod
    async def remove_tag_from_event(
        session: AsyncSession, event_id: str, tag_id: str
    ) -> Event | None:
        event = await EventRepository.get_event_by_id(session, event_id)
        if not event:
            return None

        event.tags = [t for t in event.tags if t.id != tag_id]
        await session.commit()
        await session.refresh(event, attribute_names=["tags"])
        return event
