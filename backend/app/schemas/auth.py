from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    age: int | None = Field(None, ge=1, le=150)
    height: int | None = Field(None, ge=50, le=300)  # cm
    weight: int | None = Field(None, ge=10, le=500)  # kg


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    age: int | None = None
    height: int | None = None
    weight: int | None = None
    role: str
    created_at: datetime | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | None, _info) -> str | None:
        if value is None:
            return None
        return value.isoformat()


class AuthResponse(TokenResponse):
    user: UserResponse
