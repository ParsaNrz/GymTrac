from pydantic import BaseModel, Field, ConfigDict
from typing import List


class WorkoutDayExerciseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    display_order: int


class WorkoutDaySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weekday: str
    exercises: List[WorkoutDayExerciseSchema] = []


class WorkoutPlanSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    days: List[WorkoutDaySchema] = []


class AddExerciseToDay(BaseModel):
    exercise_id: int = Field(..., gt=0)


class ReorderRequest(BaseModel):
    exercises: List[dict] = Field(..., description="List of {exercise_id, display_order}")
