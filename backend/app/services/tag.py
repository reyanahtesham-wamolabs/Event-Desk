from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationError
from app.models.user import UserRole as Role, User
from app.repositories.tag import TagRepository as tags_repo


class TagService:
    def __init__(self, db_session: AsyncSession = None):
        self.session = db_session

    def _get_session(self, session=None) -> AsyncSession:
        sess = session or self.session
        if sess is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session missing",
            )
        return sess

    def _assert_admin(self, user: User) -> None:
        if user.role != Role.ADMIN:
            raise AuthorizationError("Only admins may manage tags")

    def _normalize(self, name: str) -> str:
        name = name.strip().lower()
        if not name:
            raise ValidationError("Tag name cannot be empty")
        if len(name) > 50:
            raise ValidationError("Tag name must be 50 characters or fewer")
        return name

    async def create_tag(self, current_user: User, name: str, session=None):
        sess = self._get_session(session)
        self._assert_admin(current_user)
        name = self._normalize(name)
        try:
            return await tags_repo.create_tag(sess, name)
        except ValueError:
            raise ConflictError(f"Tag '{name}' already exists")

    async def list_tags(self, skip: int = 0, limit: int = 100, session=None):
        sess = self._get_session(session)
        # Read-only, no restriction — any authenticated user can see available tags
        return await tags_repo.list_tags(sess, skip=skip, limit=limit)

    async def update_tag(self, current_user: User, tag_id: str, name: str, session=None):
        sess = self._get_session(session)
        self._assert_admin(current_user)
        name = self._normalize(name)

        try:
            tag = await tags_repo.update_tag(sess, tag_id, name)
        except ValueError:
            raise ConflictError(f"Tag '{name}' already exists")

        if not tag:
            raise NotFoundError(f"Tag '{tag_id}' not found")
        return tag

    async def delete_tag(self, current_user: User, tag_id: str, session=None) -> None:
        sess = self._get_session(session)
        self._assert_admin(current_user)
        deleted = await tags_repo.delete_tag(sess, tag_id)
        if not deleted:
            raise NotFoundError(f"Tag '{tag_id}' not found")
