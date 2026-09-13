from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user_from_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    # Check for duplicate username
    stmt = select(User).where(User.username == body.username)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        age=body.age,
        height=body.height,
        weight=body.weight,
        role="user",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(User).where(User.username == body.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout():
    # Stateless JWT — logout is handled on the client side.
    return {"message": "Logged out"}


@router.get("/me", response_model=AuthResponse)
async def get_me(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    # current_user is injected by the dependency; we need the token from the header.
    # The dependency already validated the token and fetched the user.
    return AuthResponse(
        access_token="",  # caller should already have the token
        user=UserResponse.model_validate(current_user),
    )
