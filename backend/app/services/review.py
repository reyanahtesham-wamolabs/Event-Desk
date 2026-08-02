from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import EventStatus
from app.models.user import User, UserRole
from app.repositories.review import ReviewRepository
from app.repositories.ticket import TicketRepository
from app.repositories.event import EventRepository
from app.utils.exceptions import NotFoundError, PermissionDeniedError, ValidationError


class ReviewService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session
        self.repo = ReviewRepository(db_session)
        self.ticket_repository = TicketRepository(db_session)

    async def create_review(self, user: User, event_id: str, review: str, rating: int):
        user_tickets = await self.ticket_repository.get_by_user(user.id)

        flag = False
        if user.role == UserRole.ADMIN:
            flag = True
        if user_tickets:
            for i in user_tickets:
                if i.event_id == event_id:
                    flag = True
        if flag == False:
            raise PermissionDeniedError("Did not attend this event cannot leave review")
        event = await EventRepository.get_event_by_id(self.session, event_id)

        if event is None:
            raise NotFoundError(f"Event '{event_id}' not found")

        if event.status not in (EventStatus.PUBLISHED, EventStatus.COMPLETED):
            raise ValidationError(
                f"Reviews can only be left on published or completed events "
                f"(current status: {event.status.value})"
            )

        return await self.repo.create(
            event_id=event_id,
            user_id=user.id,
            review=review,
            rating=rating,
        )

    async def get_review(self, review_id: str):
        return await self.repo.get(review_id)

    async def list_event_reviews(self, event_id: str):
        return await self.repo.get_by_event(event_id)

    async def list_user_reviews(self, user_id: str):
        return await self.repo.get_by_user(user_id)

    async def reply_to_review(self, user: User, review_id: str, review_text: str):
        parent = await self.repo.get(review_id)
        event = await EventRepository.get_event_by_id(self.session, parent.event_id)

        if user.role != UserRole.ADMIN and (
            event is None or event.organizer_id != user.id
        ):
            raise PermissionDeniedError(
                "Only the event organizer or an admin can reply to reviews"
            )

        return await self.repo.create_reply(
            review_id=review_id,
            user_id=user.id,
            review_text=review_text,
        )

    async def update_review(self, user: User, review_id: str, **fields):
        review = await self.repo.get(review_id)

        if user.role == UserRole.ADMIN:
            pass  # admin can edit any review
        elif review.user_id == user.id:
            pass  # owner can edit own review
        else:
            raise PermissionDeniedError("You cannot edit this review")

        return await self.repo.update(review_id, **fields)

    async def delete_review(self, user: User, review_id: str):
        review = await self.repo.get(review_id)

        if user.role == UserRole.ADMIN:
            pass  # admin can delete any review
        elif review.user_id == user.id:
            pass  # owner can delete own review
        else:
            raise PermissionDeniedError("You cannot delete this review")

        return await self.repo.delete(review_id)
