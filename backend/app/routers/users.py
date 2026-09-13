from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.schemas.user import UserUpdate
from app.schemas.auth import UserResponse
from app.dependencies import get_current_user_from_token
from app.services.auth_service import hash_password, verify_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    body: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    update_data = body.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"] is not None:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    if "username" in update_data and update_data["username"] is not None:
        # Check for duplicate username (excluding self)
        stmt = select(User).where(User.username == update_data["username"], User.id != current_user.id)
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await session.commit()
    await session.refresh(current_user)
    return UserResponse.model_validate(current_user)
