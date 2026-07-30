from fastapi import APIRouter, Depends, HTTPException

from app.core.permissions import Permission
from app.dependencies.authorization import get_current_user, require_permission
from app.dependencies.services import get_review_service
from app.models.user import User
from app.schemas.review import ReviewResponse, ReviewUpdate, ReviewReply
from app.services.review import ReviewService
from app.utils.exceptions import NotFoundError, PermissionDeniedError

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
):
    try:
        return await review_service.reply_to_review(user, review_id, payload.review)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except PermissionDeniedError as e:
        raise HTTPException(403, str(e))
