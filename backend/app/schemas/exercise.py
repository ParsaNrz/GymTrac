from datetime import datetime
from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional

VALID_MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps",
    "Legs", "Glutes", "Calves", "Abs", "Forearms",
]


class ExerciseSchema(BaseModel):
    id: int
    name: str
    primary_muscle_group: str
    equipment: str | None = None
    description: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("created_at", mode="before")
    @classmethod
    def convert_created_at(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | str | None, _info) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


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
