from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutDay, WorkoutDayExercise, WorkoutPlan as WPModel
from app.models.exercise import Exercise
from app.schemas.calendar import CalendarDaySchema, CalendarResponse
from app.dependencies import get_current_user_from_token

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


async def _get_or_create_plan(session: AsyncSession, user: User) -> WPModel:
    """Reuse the same logic as the workout router: get existing plan or create one."""
    stmt = select(WorkoutPlan).where(WorkoutPlan.user_id == user.id)
    result = await session.execute(stmt)
    plan = result.scalar_one_or_none()

    if plan is None:
        plan = WorkoutPlan(user_id=user.id)
        session.add(plan)
        await session.flush()
        await session.refresh(plan)

        # Create 7 empty days
        for day_name in WEEKDAYS:
            day = WorkoutDay(workout_plan_id=plan.id, weekday=day_name)
            session.add(day)
        await session.commit()
        await session.refresh(plan)

    return plan


async def _build_calendar_response(
    session: AsyncSession, plan: WPModel
) -> CalendarResponse:
    """Build the calendar response from the user's workout plan."""
    days_stmt = select(WorkoutDay).where(
        WorkoutDay.workout_plan_id == plan.id
    )
    days_result = await session.execute(days_stmt)
    days = days_result.scalars().all()

    # Sort days by WEEKDAYS order
    day_order = {name: i for i, name in enumerate(WEEKDAYS)}
    days = sorted(days, key=lambda d: day_order.get(d.weekday, 99))

    day_schemas = []
    for day in days:
        ex_stmt = (
            select(WorkoutDayExercise)
            .where(WorkoutDayExercise.workout_day_id == day.id)
            .order_by(WorkoutDayExercise.display_order)
        )
        ex_result = await session.execute(ex_stmt)
        exercises = ex_result.scalars().all()

        exercise_details = []
        for ex_assignment in exercises:
            ex_detail_stmt = select(Exercise).where(
                Exercise.id == ex_assignment.exercise_id
            )
            ex_detail_result = await session.execute(ex_detail_stmt)
            exercise = ex_detail_result.scalar_one_or_none()
            exercise_details.append({
                "assignment_id": ex_assignment.id,
                "exercise_id": ex_assignment.exercise_id,
                "exercise_name": exercise.name if exercise else f"Exercise #{ex_assignment.exercise_id}",
                "primary_muscle_group": exercise.primary_muscle_group if exercise else None,
                "equipment": exercise.equipment if exercise else None,
                "description": exercise.description if exercise else None,
                "display_order": ex_assignment.display_order,
                "sets": ex_assignment.sets,
                "reps": ex_assignment.reps,
                "notes": ex_assignment.notes,
            })

        day_schemas.append(CalendarDaySchema(
            weekday=day.weekday,
            exercises=exercise_details,
            exercise_count=len(exercises),
        ))

    return CalendarResponse(days=day_schemas)


@router.get("/")
async def get_calendar(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_from_token),
) -> CalendarResponse:
    """Return the authenticated user's weekly workout schedule in calendar format.

    Returns all 7 days of the week with their assigned exercises,
    including exercise names, muscle groups, equipment, and workout details
    (sets, reps, notes).

    If the user has no workout plan yet, one is created automatically
    (same behavior as the /api/workout/plan endpoint) with 7 empty days.
    """
    plan = await _get_or_create_plan(session, current_user)
    return await _build_calendar_response(session, plan)
