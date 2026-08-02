from pydantic import BaseModel,Field

class TagResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


