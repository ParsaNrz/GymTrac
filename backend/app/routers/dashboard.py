from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_async_session
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutDay, WorkoutDayExercise
from app.dependencies import get_current_user_from_token

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _today_weekday() -> str:
    """Return today's weekday name (Monday=0 convention matches Python's weekday())."""
    return WEEKDAYS[datetime.today().weekday()]


@router.get("/")
async def get_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """Return the authenticated user's profile and workout-plan summary.

    This is a lightweight consolidated endpoint for the dashboard page.
    It does NOT return the full list of exercises per day — use /api/workout/plan
    for that. The summary includes today's exercise count and whether today is a
    rest day.
    """
    # --- User profile ---
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "age": current_user.age,
        "height": current_user.height,
        "weight": current_user.weight,
        "role": current_user.role,
    }

    # --- Workout plan ---
    plan_stmt = select(WorkoutPlan).where(WorkoutPlan.user_id == current_user.id)
    plan_result = await session.execute(plan_stmt)
    plan = plan_result.scalar_one_or_none()

    if plan is None:
        return {
            "user": user_data,
            "plan_summary": {
                "plan_id": None,
                "total_days": 0,
                "total_exercises": 0,
                "today_weekday": _today_weekday(),
                "today_exercises_count": 0,
                "is_rest_day": True,
            },
        }

    # Total exercise assignments across all days
    total_stmt = select(WorkoutDayExercise).where(
        WorkoutDayExercise.workout_day_id.in_(
            select(WorkoutDay.id).where(WorkoutDay.workout_plan_id == plan.id)
        )
    )
    total_result = await session.execute(total_stmt)
    total_exercises = len(total_result.scalars().all())

    # Day count
    days_stmt = select(WorkoutDay).where(WorkoutDay.workout_plan_id == plan.id)
    days_result = await session.execute(days_stmt)
    total_days = len(days_result.scalars().all())

    # Today's status
    today_name = _today_weekday()
    today_stmt = select(WorkoutDay).where(
        WorkoutDay.workout_plan_id == plan.id,
        WorkoutDay.weekday == today_name,
    )
    today_result = await session.execute(today_stmt)
    today_day = today_result.scalar_one_or_none()

    today_exercises_count = 0
    is_rest_day = True
    if today_day is not None:
        ex_stmt = select(WorkoutDayExercise).where(
            WorkoutDayExercise.workout_day_id == today_day.id
        )
        ex_result = await session.execute(ex_stmt)
        today_exercises = ex_result.scalars().all()
        today_exercises_count = len(today_exercises)
        is_rest_day = today_exercises_count == 0

    return {
        "user": user_data,
        "plan_summary": {
            "plan_id": plan.id,
            "total_days": total_days,
            "total_exercises": total_exercises,
            "today_weekday": today_name,
            "today_exercises_count": today_exercises_count,
            "is_rest_day": is_rest_day,
        },
    }
