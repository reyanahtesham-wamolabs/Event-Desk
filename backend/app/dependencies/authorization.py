from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.services.jwt import TokenFunctionality
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    token: str = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> User:
    try:
        token_result = await TokenFunctionality.ensure_valid_access_token(token.credentials, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    if token_result["status"] == "login_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_result["status"] == "refresh_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Refresh required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = token_result["payload"]["sub"]
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
