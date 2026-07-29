from fastapi import APIRouter, Depends

from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import RefreshToken
from app.services.auth import UserAuthenticationServices
from app.dependencies.services import get_auth_service
from app.dependencies.authorization import get_current_user
from app.models.user import User as db_User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(
    user_data: UserCreate,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.user_signup(user_data)


@router.post("/login")
async def login(
    user_data: UserLogin,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.user_login(user_data)


@router.post("/logout")
async def logout(
    current_user: db_User = Depends(get_current_user),
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.user_logout(current_user)


@router.post("/refresh")
async def refresh(
    token: RefreshToken,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.refresh_token(token.refresh_token)
