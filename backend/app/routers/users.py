from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.settings import ChangePasswordRequest, ChangePasswordResponse
from app.schemas.user import UserUpdate
from app.dependencies import get_current_user_from_token
from app.services.auth_service import verify_password, hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """Return the authenticated user's own profile.

    Returns username, age, height, weight, role, and created_at.
    Does NOT return password_hash or any password-related data.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    body: UserUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """Update the authenticated user's editable profile fields.

    Allowed fields: username, age, height, weight.
    Role cannot be changed by normal users.
    Password changes must go through POST /api/users/change-password.
    """
    update_data = body.model_dump(exclude_unset=True)

    # Remove password from profile update — must use change-password endpoint
    update_data.pop("password", None)

    if "username" in update_data and update_data["username"] is not None:
        # Check for duplicate username (excluding self)
        stmt = select(User).where(
            User.username == update_data["username"],
            User.id != current_user.id,
        )
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


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    body: ChangePasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """Change the authenticated user's password.

    Requires the current password to be provided and verified.
    The new password is hashed with bcrypt and stored.
    """
    # Verify current password
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Hash and store new password
    current_user.password_hash = hash_password(body.new_password)
    await session.commit()

    return ChangePasswordResponse(success=True, message="Password changed successfully")
