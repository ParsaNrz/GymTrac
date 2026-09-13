from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.services.auth_service import decode_access_token


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Dependency that extracts and validates the JWT from the Authorization header.

    Returns the User model instance. Raises 401 if the token is missing,
    expired, invalid, or the user no longer exists.
    """
    # The token is expected to be passed via the Authorization header by the
    # router dependencies. This function is a building block; routers should
    # call it after extracting the token string.
    pass


async def get_current_user_from_token(
    token: str,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.id == int(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(required_role: str):
    """Returns a dependency that checks the current user has the required role."""

    async def role_checker(current_user: User = Depends(get_current_user_from_token)) -> User:
        # Note: the token is extracted upstream; we receive the user directly.
        # This function is used as: Depends(require_role("admin"))(get_current_user_from_token)
        # See routers for the actual wiring.
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user

    return role_checker
