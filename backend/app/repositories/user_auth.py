from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as db_User,UserRole

class UserCrud:
    @staticmethod
    async def add_user(
        name: str,
        email: str,
        password_hash: str,
        role:UserRole,
        session: AsyncSession,
    ) -> db_User:
        user = db_User(name=name, email=email, password_hash=password_hash,role=role)
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> db_User | None:
        try:
            stmt = select(db_User).where(db_User.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    @staticmethod
    async def get_user_by_id(user_id: str, session: AsyncSession) -> db_User | None:
        try:
            stmt = select(db_User).where(db_User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise
