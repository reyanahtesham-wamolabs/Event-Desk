from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationType
from app.models.user import User, UserRole
from app.repositories.notification import NotificationRepository
from app.utils.exceptions import PermissionDeniedError

class NotificationService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session
        self.repo = NotificationRepository(db_session)

    async def get_notification(self, user: User, notification_id: str):
        notification = await self.repo.get(notification_id)
        if user.role != UserRole.ADMIN and notification.user_id != user.id:
            raise PermissionDeniedError("You cannot view this notification")
        return notification

    async def list_my_notifications(
        self,
        user_id: str,
        notification_type: NotificationType | None = None,
    ):
        return await self.repo.get_by_user(user_id, notification_type=notification_type)

    async def mark_as_read(self, user: User, notification_id: str):
        notification = await self.repo.get(notification_id)
        if user.role != UserRole.ADMIN and notification.user_id != user.id:
            raise PermissionDeniedError("You cannot modify this notification")
        return await self.repo.mark_as_read(notification_id)

    async def mark_as_unread(self, user: User, notification_id: str):
        notification = await self.repo.get(notification_id)
        if user.role != UserRole.ADMIN and notification.user_id != user.id:
            raise PermissionDeniedError("You cannot modify this notification")
        return await self.repo.mark_as_unread(notification_id)

    async def delete_notification(self, user: User, notification_id: str):
        notification = await self.repo.get(notification_id)
        if user.role != UserRole.ADMIN and notification.user_id != user.id:
            raise PermissionDeniedError("You cannot delete this notification")
        return await self.repo.delete(notification_id)

    async def clear_my_notifications(self, user_id: str) -> int:
        return await self.repo.delete_all_by_user(user_id)
