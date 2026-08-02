"""
Background notification helpers.

These functions create their own DB sessions so they can safely run
inside FastAPI's BackgroundTasks after the request session is closed.
"""

from app.models.database import AsyncSessionLocal
from app.models.notification import NotificationType
from app.repositories.notification import NotificationRepository


async def send_notification(
    user_id: str,
    notification_type: NotificationType,
    message: str,
    event_id: str | None = None,
) -> None:
    """Send a single notification in the background."""
    async with AsyncSessionLocal() as session:
        repo = NotificationRepository(session)
        await repo.create(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            event_id=event_id,
        )


async def send_bulk_notifications(
    notifications: list[dict],
) -> None:
    """
    Send multiple notifications in the background.

    Each dict should have keys: user_id, type, message, and optionally event_id.
    """
    if not notifications:
        return
    async with AsyncSessionLocal() as session:
        repo = NotificationRepository(session)
        await repo.bulk_create(notifications)
