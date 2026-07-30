from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    review: str
    rating: int = Field(ge=1, le=5)


class ReviewUpdate(BaseModel):
    review: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)


class ReviewReply(BaseModel):
    review: str


class ReviewResponse(BaseModel):
    id: str
    review: str
    rating: int
    reply_id: str | None
    user_id: str | None
    event_id: str

    class Config:
        from_attributes = True
