from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise import ExerciseSchema, CreateExerciseRequest, UpdateExerciseRequest
from app.dependencies import get_current_user_from_token, require_role

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

VALID_MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps",
    "Legs", "Glutes", "Calves", "Abs", "Forearms",
]


def _validate_muscle_group(group: str) -> str:
    if group not in VALID_MUSCLE_GROUPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid muscle group. Must be one of: {', '.join(VALID_MUSCLE_GROUPS)}",
        )
    return group


@router.get("", response_model=list[ExerciseSchema])
async def list_exercises(
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    muscle_group: Optional[str] = Query(None, max_length=30),
    equipment: Optional[str] = Query(None, max_length=50),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """List exercises. Requires login (any role). Admins can also write."""
    query = select(Exercise)

    if search:
        query = query.where(Exercise.name.ilike(f"%{search}%"))
    if muscle_group:
        if muscle_group not in VALID_MUSCLE_GROUPS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid muscle_group filter. Must be one of: {', '.join(VALID_MUSCLE_GROUPS)}",
            )
        query = query.where(Exercise.primary_muscle_group == muscle_group)
    if equipment:
        query = query.where(Exercise.equipment.ilike(f"%{equipment}%"))

    query = query.order_by(Exercise.name)
    result = await session.execute(query)
    exercises = result.scalars().all()
    return [ExerciseSchema.model_validate(e) for e in exercises]


@router.get("/muscle-groups", response_model=list[str])
async def list_muscle_groups(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """Return the list of valid muscle groups."""
    return VALID_MUSCLE_GROUPS


@router.get("/categories", response_model=list[str])
async def list_categories():
    """Alias for muscle groups — kept for frontend convenience."""
    return VALID_MUSCLE_GROUPS


@router.get("/{exercise_id}", response_model=ExerciseSchema)
async def get_exercise(
    exercise_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await session.execute(stmt)
    exercise = result.scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return ExerciseSchema.model_validate(exercise)


# ---- Admin write operations (also reachable via /api/admin/exercises) ----

@router.post("", response_model=ExerciseSchema, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    body: CreateExerciseRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_role("admin")),
):
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


@router.put("/{exercise_id}", response_model=ExerciseSchema)
async def update_exercise(
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
        _validate_muscle_group(update_data["primary_muscle_group"])

    for field, value in update_data.items():
        setattr(exercise, field, value)

    await session.commit()
    await session.refresh(exercise)
    return ExerciseSchema.model_validate(exercise)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
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
