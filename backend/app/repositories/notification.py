import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType
from app.utils.exceptions import NotFoundError


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: str,
        notification_type: NotificationType,
        message: str,
        event_id: str | None = None,
    ) -> Notification:
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            event_id=event_id,
            type=notification_type,
            message=message,
            is_read=False,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def bulk_create(
        self,
        notifications: list[dict],
    ) -> list[Notification]:
        objs = [
            Notification(
                id=str(uuid.uuid4()),
                user_id=n["user_id"],
                event_id=n.get("event_id"),
                type=n["type"],
                message=n.get("message", ""),
                is_read=False,
            )
            for n in notifications
        ]
        self.db.add_all(objs)
        await self.db.commit()
        return objs

    async def get(self, notification_id: str) -> Notification:
        notification = await self.db.get(Notification, notification_id)
        if not notification:
            raise NotFoundError(f"Notification '{notification_id}' not found")
        return notification

    async def get_by_user(
        self,
        user_id: str,
        notification_type: NotificationType | None = None,
    ) -> Sequence[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
        )
        if notification_type is not None:
            stmt = stmt.where(Notification.type == notification_type)
        stmt = stmt.order_by(Notification.id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_event(self, event_id: str) -> Sequence[Notification]:
        stmt = select(Notification).where(Notification.event_id == event_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, notification_id: str) -> Notification:
        notification = await self.get(notification_id)
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_as_unread(self, notification_id: str) -> Notification:
        notification = await self.get(notification_id)
        notification.is_read = False
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete(self, notification_id: str) -> None:
        notification = await self.get(notification_id)
        await self.db.delete(notification)
        await self.db.commit()

    async def delete_all_by_user(self, user_id: str) -> int:
        notifications = await self.get_by_user(user_id)
        count = len(notifications)
        for n in notifications:
            await self.db.delete(n)
        await self.db.commit()
        return count
