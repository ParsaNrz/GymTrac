import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_async_session
from app.models.user import User
from app.services.auth_service import hash_password, create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./data/gym_trac_test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_async_session():
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provide a database session for tests."""
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession):
    """Create a regular user and return it."""
    user = User(
        username="testuser",
        password_hash=hash_password("password123"),
        age=25,
        height=175,
        weight=70,
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Create an admin user and return it."""
    user = User(
        username="adminuser",
        password_hash=hash_password("adminpass123"),
        age=30,
        height=180,
        weight=80,
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession):
    """Create another regular user and return it."""
    user = User(
        username="anotheruser",
        password_hash=hash_password("anotherpass123"),
        age=22,
        height=165,
        weight=60,
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def create_test_token(user: User) -> str:
    """Create a valid JWT for a user."""
    return create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
