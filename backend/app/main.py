from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, workout, exercises, admin, dashboard
from app.services.seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed initial admin (idempotent)
    await seed_admin()
    yield


app = FastAPI(title="GymTrac API", lifespan=lifespan)

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


@app.get("/health")
async def health():
    return {"status": "ok"}
