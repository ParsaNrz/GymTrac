from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(None, ge=1, le=150)
    height: Optional[int] = Field(None, ge=50, le=300)
    weight: Optional[int] = Field(None, ge=10, le=500)
    # Password is NOT allowed in profile update — use change-password endpoint
    password: Optional[str] = None  # deprecated, ignored


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


class ChangePasswordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool
    message: str
