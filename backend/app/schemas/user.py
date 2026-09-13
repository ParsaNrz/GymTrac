from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    age: int | None = Field(None, ge=1, le=150)
    height: int | None = Field(None, ge=50, le=300)
    weight: int | None = Field(None, ge=10, le=500)
    password: str | None = Field(None, min_length=6, max_length=128)
