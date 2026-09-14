from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func

from app.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)
    weekday = Column(String(10), nullable=False)

    __table_args__ = (
        UniqueConstraint("workout_plan_id", "weekday", name="uq_workout_days_plan_weekday"),
    )


class WorkoutDayExercise(Base):
    __tablename__ = "workout_day_exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_day_id = Column(Integer, ForeignKey("workout_days.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
