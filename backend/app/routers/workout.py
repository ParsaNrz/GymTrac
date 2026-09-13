from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutDay, WorkoutDayExercise
from app.models.exercise import Exercise
from app.schemas.workout import (
    WorkoutPlanSchema,
    WorkoutDaySchema,
    WorkoutDayExerciseSchema,
    AddExerciseToDay,
    ReorderRequest,
)
from app.dependencies import get_current_user_from_token

router = APIRouter(prefix="/api/workout", tags=["workout"])

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


async def get_or_create_plan(session: AsyncSession, user: User) -> WorkoutPlan:
    stmt = select(WorkoutPlan).where(WorkoutPlan.user_id == user.id)
    result = await session.execute(stmt)
    plan = result.scalar_one_or_none()

    if plan is None:
        plan = WorkoutPlan(user_id=user.id)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)

        # Create the seven empty weekdays
        for day_name in WEEKDAYS:
            day = WorkoutDay(workout_plan_id=plan.id, weekday=day_name)
            session.add(day)
        await session.commit()

    return plan


def _build_plan_response(session: AsyncSession, plan: WorkoutPlan) -> WorkoutPlanSchema:
    days_stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id)
    days_result = await session.execute(days_stmt)
    days = days_result.scalars().all()

    day_schemas = []
    for day in days:
        ex_stmt = (
            select(WorkoutDayExercise)
            .where(WorkoutDayExercise.workout_day_id == day.id)
            .order_by(WorkoutDayExercise.display_order)
        )
        ex_result = await session.execute(ex_stmt)
        exercises = ex_result.scalars().all()
        day_schemas.append(
            WorkoutDaySchema(
                id=day.id,
                weekday=day.weekday,
                exercises=[WorkoutDayExerciseSchema.model_validate(e) for e in exercises],
            )
        )

    return WorkoutPlanSchema(
        id=plan.id,
        user_id=plan.user_id,
        days=day_schemas,
    )


@router.get("/plan", response_model=WorkoutPlanSchema)
async def get_plan(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    plan = await get_or_create_plan(session, current_user)
    return await _build_plan_response(session, plan)


@router.put("/plan", response_model=WorkoutPlanSchema)
async def replace_plan(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    # For V1, a full replace is not exposed; the plan is managed per-day.
    # This endpoint can be used in the future for full plan import/export.
    plan = await get_or_create_plan(session, current_user)
    return await _build_plan_response(session, plan)


@router.get("/day/{weekday}", response_model=WorkoutDaySchema)
async def get_day(
    weekday: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    if weekday not in WEEKDAYS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid weekday: {weekday}")

    plan = await get_or_create_plan(session, current_user)

    stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id, WorkoutDay.weekday == weekday)
    result = await session.execute(stmt)
    day = result.scalar_one_or_none()

    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

    ex_stmt = (
        select(WorkoutDayExercise)
        .where(WorkoutDayExercise.workout_day_id == day.id)
        .order_by(WorkoutDayExercise.display_order)
    )
    ex_result = await session.execute(ex_stmt)
    exercises = ex_result.scalars().all()

    return WorkoutDaySchema(
        id=day.id,
        weekday=day.weekday,
        exercises=[WorkoutDayExerciseSchema.model_validate(e) for e in exercises],
    )


@router.post("/day/{weekday}/exercises", response_model=WorkoutDaySchema)
async def add_exercise_to_day(
    weekday: str,
    body: AddExerciseToDay,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    if weekday not in WEEKDAYS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid weekday: {weekday}")

    # Verify exercise exists
    ex_stmt = select(Exercise).where(Exercise.id == body.exercise_id)
    ex_result = await session.execute(ex_stmt)
    exercise = ex_result.scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    plan = await get_or_create_plan(session, current_user)

    day_stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id, WorkoutDay.weekday == weekday)
    day_result = await session.execute(day_stmt)
    day = day_result.scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

    # Check duplicate
    dup_stmt = select(WorkoutDayExercise).where(
        WorkoutDayExercise.workout_day_id == day.id,
        WorkoutDayExercise.exercise_id == body.exercise_id,
    )
    dup_result = await session.execute(dup_stmt)
    if dup_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exercise already assigned to this day")

    # Compute next display_order
    order_stmt = select(WorkoutDayExercise).where(WorkoutDayExercise.workout_day_id == day.id)
    order_result = await session.execute(order_stmt)
    existing = order_result.scalars().all()
    next_order = max((e.display_order for e in existing), default=-1) + 1

    assignment = WorkoutDayExercise(
        workout_day_id=day.id,
        exercise_id=body.exercise_id,
        display_order=next_order,
    )
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)

    return await get_day(session, weekday, current_user)


@router.delete("/day/{weekday}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_exercise_from_day(
    weekday: str,
    exercise_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    if weekday not in WEEKDAYS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid weekday: {weekday}")

    plan = await get_or_create_plan(session, current_user)

    day_stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id, WorkoutDay.weekday == weekday)
    day_result = await session.execute(day_stmt)
    day = day_result.scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

    del_stmt = select(WorkoutDayExercise).where(
        WorkoutDayExercise.workout_day_id == day.id,
        WorkoutDayExercise.exercise_id == exercise_id,
    )
    del_result = await session.execute(del_stmt)
    assignment = del_result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found on this day")

    await session.delete(assignment)
    await session.commit()


@router.put("/day/{weekday}/order", response_model=WorkoutDaySchema)
async def reorder_day_exercises(
    weekday: str,
    body: ReorderRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    if weekday not in WEEKDAYS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid weekday: {weekday}")

    plan = await get_or_create_plan(session, current_user)

    day_stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id, WorkoutDay.weekday == weekday)
    day_result = await session.execute(day_stmt)
    day = day_result.scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

    for item in body.exercises:
        ex_id = item.get("exercise_id")
        new_order = item.get("display_order")
        if ex_id is None or new_order is None:
            continue
        up_stmt = select(WorkoutDayExercise).where(
            WorkoutDayExercise.workout_day_id == day.id,
            WorkoutDayExercise.exercise_id == ex_id,
        )
        up_result = await session.execute(up_stmt)
        entry = up_result.scalar_one_or_none()
        if entry is not None:
            entry.display_order = new_order

    await session.commit()
    return await get_day(session, weekday, current_user)
