from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.permissions import Permission
from app.dependencies.authorization import require_permission
from app.dependencies.services import get_notification_service
from app.models.notification import NotificationType
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService
from app.utils.exceptions import NotFoundError, PermissionDeniedError

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/my-notifications", response_model=list[NotificationResponse])
async def list_my_notifications(
    type: NotificationType | None = Query(default=None),
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.list_my_notifications(
        user.id, notification_type=type
    )

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        return await notification_service.get_notification(user, notification_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: str,
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        return await notification_service.mark_as_read(user, notification_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))

@router.patch("/{notification_id}/unread", response_model=NotificationResponse)
async def mark_as_unread(
    notification_id: str,
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        return await notification_service.mark_as_unread(user, notification_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))

@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: str,
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    try:
        await notification_service.delete_notification(user, notification_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))

@router.delete("", status_code=204)
async def clear_my_notifications(
    user: User = Depends(require_permission(Permission.VIEW_OWN_NOTIFICATIONS)),
    notification_service: NotificationService = Depends(get_notification_service),
):
    await notification_service.clear_my_notifications(user.id)
