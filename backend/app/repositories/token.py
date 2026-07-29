from __future__ import annotations
from datetime import datetime, UTC
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken as db_RefreshToken


class tokenCRUD:
    @staticmethod
    async def add_token(JWT_token: str, user_id: str, expire_time: datetime, session: AsyncSession):
        refresh_token = db_RefreshToken(user_id=user_id, token=JWT_token, expire_time=expire_time)
        try:
            session.add(refresh_token)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def get_valid_refresh_token(user_id: str, session: AsyncSession) -> db_RefreshToken | None:
        try:
            stmt = select(db_RefreshToken).where(
                db_RefreshToken.user_id == user_id,
                db_RefreshToken.expire_time > datetime.now(UTC),
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    @staticmethod
    async def token_exists(user_id: str, session: AsyncSession) -> bool:
        try:
            stmt = select(db_RefreshToken).where(
                db_RefreshToken.user_id == user_id,
                db_RefreshToken.expire_time > datetime.now(UTC),
            )
            result = await session.execute(stmt)
            token_obj = result.scalar_one_or_none()
            return token_obj is not None
        except SQLAlchemyError:
            raise

    @staticmethod
    async def delete_refresh_token(user_id: str, session: AsyncSession):
        try:
            stmt = sa.delete(db_RefreshToken).where(db_RefreshToken.user_id == user_id)
            await session.execute(stmt)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
