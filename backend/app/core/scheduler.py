"""
APScheduler-based background tasks.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.models.database import AsyncSessionLocal
from app.models.notification import NotificationType
from app.repositories.notification import NotificationRepository


scheduler = AsyncIOScheduler()


async def _send_notification_job(
    user_id: str,
    notification_type: NotificationType,
    message: str,
    event_id: str | None = None,
) -> None:
    async with AsyncSessionLocal() as session:
        repo = NotificationRepository(session)
        await repo.create(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            event_id=event_id,
        )


async def _send_bulk_notifications_job(
    notifications: list[dict],
) -> None:
    if not notifications:
        return
    async with AsyncSessionLocal() as session:
        repo = NotificationRepository(session)
        await repo.bulk_create(notifications)


def schedule_notification(
    user_id: str,
    notification_type: NotificationType,
    message: str,
    event_id: str | None = None,
) -> None:
    scheduler.add_job(
        _send_notification_job,
        args=[user_id, notification_type, message, event_id]
    )


def schedule_bulk_notifications(notifications: list[dict]) -> None:
    if notifications:
        scheduler.add_job(
            _send_bulk_notifications_job,
            args=[notifications]
        )
