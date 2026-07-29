from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Tag

class TagRepository():
    async def create_tag(session: AsyncSession, name: str) -> Tag:
        """Create a new tag. Raises ValueError if the name already exists."""
        tag = Tag(name=name)
        session.add(tag)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError(f"Tag '{name}' already exists")
        await session.refresh(tag)
        return tag


    async def get_tag_by_id(session: AsyncSession, tag_id: str) -> Tag | None:
        return await session.get(Tag, tag_id)


    async def get_tag_by_name(session: AsyncSession, name: str) -> Tag | None:
        result = await session.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()


    async def get_or_create_tag(session: AsyncSession, name: str) -> Tag:
        """Idempotent helper — useful when attaching tags to events by name."""
        tag = await TagRepository.get_tag_by_name(session, name)
        if tag:
            return tag
        return await TagRepository.create_tag(session, name)


    async def list_tags(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Tag]:
        result = await session.execute(select(Tag).offset(skip).limit(limit))
        return list(result.scalars().all())


    async def update_tag(session: AsyncSession, tag_id: str, name: str) -> Tag | None:
        tag = await session.get(Tag, tag_id)
        if not tag:
            return None
        tag.name = name
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError(f"Tag '{name}' already exists")
        await session.refresh(tag)
        return tag


    async def delete_tag(session: AsyncSession, tag_id: str) -> bool:
        tag = await session.get(Tag, tag_id)
        if not tag:
            return False
        await session.delete(tag)
        await session.commit()
        return True