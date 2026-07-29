from pydantic import BaseModel


class jwtTokensModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
