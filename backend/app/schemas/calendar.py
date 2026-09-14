from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class CalendarExerciseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignment_id: int
    exercise_id: int
    exercise_name: str
    primary_muscle_group: Optional[str] = None
    equipment: Optional[str] = None
    description: Optional[str] = None
    display_order: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    notes: Optional[str] = None


class CalendarDaySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    weekday: str
    exercises: List[CalendarExerciseSchema] = []
    exercise_count: int = 0


class CalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    days: List[CalendarDaySchema] = []
