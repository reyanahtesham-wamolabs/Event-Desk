from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationCreate(BaseModel):
    user_id: str
    event_id: str | None = None
    type: NotificationType
    message: str


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    event_id: str | None
    type: NotificationType
    message: str
    is_read: bool

    class Config:
        from_attributes = True
