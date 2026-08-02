from fastapi import APIRouter, Depends, HTTPException
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db

from app.core.permissions import Permission
from app.dependencies.authorization import get_current_user, require_permission
from app.dependencies.services import get_review_service
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.review import ReviewResponse, ReviewUpdate, ReviewReply
from app.services.review import ReviewService
from app.utils.exceptions import NotFoundError, PermissionDeniedError
from app.models.notification import NotificationType
from app.core.scheduler import schedule_notification, schedule_bulk_notifications

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/my-reviews", response_model=list[ReviewResponse])
async def list_my_reviews(
    user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    return await review_service.list_user_reviews(user.id)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        return await review_service.get_review(review_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    payload: ReviewUpdate,
    user: User = Depends(require_permission(Permission.EDIT_OWN_REVIEW)),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        fields = payload.model_dump(exclude_unset=True)
        return await review_service.update_review(user, review_id, **fields)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: str,
    user: User = Depends(require_permission(Permission.EDIT_OWN_REVIEW)),
    review_service: ReviewService = Depends(get_review_service),
):
    try:
        await review_service.delete_review(user, review_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))


@router.post("/{review_id}/reply", response_model=ReviewResponse, status_code=201)
async def reply_to_review(
    review_id: str,
    payload: ReviewReply,
    user: User = Depends(require_permission(Permission.REPLY_TO_REVIEW)),
    review_service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Get the parent review to find the original author
        parent_review = await review_service.get_review(review_id)
        reply = await review_service.reply_to_review(user, review_id, payload.review)
        # Notify the original review author in the background
        if parent_review.user_id and parent_review.user_id != user.id:
            schedule_notification(
                user_id=parent_review.user_id,
                notification_type=NotificationType.REVIEW_REPLY,
                message="Your review received a reply.",
                event_id=parent_review.event_id,
            )
            
        # Extract mentions and notify users
        mentioned_names = list(set(re.findall(r"@(\w+)", payload.review)))
        if mentioned_names:
            user_repo = UserRepository(db)
            mentioned_users = await user_repo.get_users_by_names(mentioned_names)
            mentioned_ids = {u.id for u in mentioned_users if u.id != user.id}
            
            if mentioned_ids:
                mentions = [
                    {
                        "user_id": uid,
                        "type": NotificationType.REVIEW_MENTION,
                        "message": f"{user.name} mentioned you in a reply to a review.",
                        "event_id": parent_review.event_id,
                    }
                    for uid in mentioned_ids
                ]
                schedule_bulk_notifications(mentions)
                
        return reply
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))
