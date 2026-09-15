from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, workout, exercises, admin, dashboard, calendar
from app.services.seed import seed_admin
from app.services.seed_exercises import seed_exercises


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Ensure existing databases have all columns expected by current models
    await _migrate_columns()
    # Seed initial admin (idempotent)
    await seed_admin()
    await seed_exercises()
    yield


app = FastAPI(title="GymTrac API", lifespan=lifespan)


async def _migrate_columns() -> None:
    """Add any columns missing from existing tables so an older database
    can be upgraded to the current schema without data loss."""
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))

        # ---- workout_day_exercises ----
        # Snapshot current columns
        result = await conn.execute(text("PRAGMA table_info(workout_day_exercises)"))
        existing_cols = {row[1] for row in result.fetchall()}  # name is column index 1

        for col_name, col_def in [
            ("sets", "INTEGER"),
            ("reps", "INTEGER"),
            ("notes", "TEXT"),
        ]:
            if col_name not in existing_cols:
                await conn.execute(
                    text(f'ALTER TABLE workout_day_exercises ADD COLUMN "{col_name}" {col_def}')
                )


# CORS: allow the Vite dev server (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workout.router)
app.include_router(exercises.router)
app.include_router(dashboard.router)
app.include_router(calendar.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
