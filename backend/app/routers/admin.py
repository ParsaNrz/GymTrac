from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.models.exercise import Exercise
from app.schemas.auth import UserResponse
from app.schemas.exercise import ExerciseSchema, CreateExerciseRequest, UpdateExerciseRequest
from app.dependencies import get_current_user_from_token, require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------- User management ----------


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    search: Optional[str] = Query(None, min_length=1, max_length=50),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    query = select(User)
    if search:
        query = query.where(User.username.ilike(f"%{search}%"))
    query = query.order_by(User.created_at.desc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await session.execute(query)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    if role not in ("user", "admin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'admin'",
        )

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = role
    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    # Prevent deleting yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Cascade: workout plan → days → day_exercises are deleted by FK cascade
    await session.delete(user)
    await session.commit()


# ---------- Exercise management (admin) ----------

# These reuse the same logic as /api/exercises but are mounted under /api/admin
# for clarity. They require the admin role explicitly here.


@router.get("/exercises", response_model=list[ExerciseSchema])
async def admin_list_exercises(
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    muscle_group: Optional[str] = Query(None, max_length=30),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    query = select(Exercise)
    if search:
        query = query.where(Exercise.name.ilike(f"%{search}%"))
    if muscle_group:
        query = query.where(Exercise.primary_muscle_group == muscle_group)
    query = query.order_by(Exercise.name)
    result = await session.execute(query)
    exercises = result.scalars().all()
    return [ExerciseSchema.model_validate(e) for e in exercises]


@router.post("/exercises", response_model=ExerciseSchema, status_code=status.HTTP_201_CREATED)
async def admin_create_exercise(
    body: CreateExerciseRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    from app.routers.exercises import _validate_muscle_group
    _validate_muscle_group(body.primary_muscle_group)

    exercise = Exercise(
        name=body.name,
        primary_muscle_group=body.primary_muscle_group,
        equipment=body.equipment,
        description=body.description,
    )
    session.add(exercise)
    await session.commit()
    await session.refresh(exercise)
    return ExerciseSchema.model_validate(exercise)


@router.put("/exercises/{exercise_id}", response_model=ExerciseSchema)
async def admin_update_exercise(
    exercise_id: int,
    body: UpdateExerciseRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await session.execute(stmt)
    exercise = result.scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    update_data = body.model_dump(exclude_unset=True)
    if "primary_muscle_group" in update_data:
        from app.routers.exercises import _validate_muscle_group
        _validate_muscle_group(update_data["primary_muscle_group"])

    for field, value in update_data.items():
        setattr(exercise, field, value)

    await session.commit()
    await session.refresh(exercise)
    return ExerciseSchema.model_validate(exercise)


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_exercise(
    exercise_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await session.execute(stmt)
    exercise = result.scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    await session.delete(exercise)
    await session.commit()
