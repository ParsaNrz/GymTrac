from pydantic import BaseModel, Field
from typing import List


class WorkoutDayExerciseSchema(BaseModel):
    id: int
    exercise_id: int
    display_order: int

    class Config:
        from_attributes = True


class WorkoutDaySchema(BaseModel):
    id: int
    weekday: str
    exercises: List[WorkoutDayExerciseSchema] = []

    class Config:
        from_attributes = True


class WorkoutPlanSchema(BaseModel):
    id: int
    user_id: int
    days: List[WorkoutDaySchema] = []

    class Config:
        from_attributes = True


class AddExerciseToDay(BaseModel):
    exercise_id: int = Field(..., gt=0)


class ReorderRequest(BaseModel):
    exercises: List[dict] = Field(..., description="List of {exercise_id, display_order}")
