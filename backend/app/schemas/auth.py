from pydantic import BaseModel, Field


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
    id: int
    username: str
    age: int | None = None
    height: int | None = None
    weight: int | None = None
    role: str
    created_at: str | None = None


class AuthResponse(TokenResponse):
    user: UserResponse
