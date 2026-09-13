from pydantic import BaseModel, Field
from typing import Optional


class ExerciseSchema(BaseModel):
    id: int
    name: str
    primary_muscle_group: str
    equipment: str | None = None
    description: str | None = None
    created_at: str | None = None

    class Config:
        from_attributes = True


class CreateExerciseRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    primary_muscle_group: str = Field(..., min_length=1, max_length=30)
    equipment: str | None = Field(None, max_length=50)
    description: str | None = Field(None)


class UpdateExerciseRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    primary_muscle_group: str | None = Field(None, min_length=1, max_length=30)
    equipment: str | None = Field(None, max_length=50)
    description: str | None = Field(None)
