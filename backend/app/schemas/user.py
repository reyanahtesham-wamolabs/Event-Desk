from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}


class SignupResponse(BaseModel):
    status: str
    user: UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str

