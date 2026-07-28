from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.user import UserCreate, UserLogin
from app.repositories.user_auth import UserCrud
from app.services.jwt import TokenFunctionality
from app.core.security import hash_password, check_password


class UserAuthenticationServices:
    def __init__(self, db_session=None):
        self.session = db_session

    def _get_session(self, session=None):
        sess = session or self.session
        if sess is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session missing",
            )
        return sess

    async def user_signup(self, user_data: UserCreate, session=None):
        sess = self._get_session(session)

        existing = await UserCrud.get_user_by_email(user_data.email, sess)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_pw = hash_password(user_data.password)

        try:
            created_user = await UserCrud.add_user(
                name=user_data.name,
                email=user_data.email,
                password_hash=hashed_pw,
                session=sess,
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            ) from e

        return {
            "status": "User created successfully",
            "user": {
                "id": created_user.id,
                "name": created_user.name,
                "email": created_user.email,
                "role": created_user.role.value if hasattr(created_user.role, "value") else str(created_user.role),
            },
        }

    async def user_login(self, user_data: UserLogin, session=None):
        sess = self._get_session(session)

        user = await UserCrud.get_user_by_email(user_data.email, sess)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not check_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = TokenFunctionality.create_access_token(user.id)
        refresh_token = await TokenFunctionality.create_refresh_token(user.id, sess)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def user_logout(self, current_user, session=None):
        sess = self._get_session(session)
        user_id = getattr(current_user, "id", current_user)
        return await TokenFunctionality.delete_token(user_id, sess)

    async def refresh_token(self, refresh_token_str: str, session=None):
        sess = self._get_session(session)
        result = await TokenFunctionality.refresh_token(refresh_token_str, sess)
        if result.get("status") == "login_required":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login required",
            )
        return result
