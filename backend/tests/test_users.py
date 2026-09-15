import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import Base, get_async_session
from app.models.user import User
from app.services.auth_service import hash_password, create_access_token
from tests.conftest import test_engine, test_session_maker, override_get_async_session, create_test_token


# Override the database dependency
app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Create all tables before each test, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def regular_user():
    """Create a regular user and return it."""
    async with test_session_maker() as session:
        user = User(
            username="testuser",
            password_hash=hash_password("password123"),
            age=25,
            height=175,
            weight=70,
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def admin_user():
    """Create an admin user and return it."""
    async with test_session_maker() as session:
        user = User(
            username="adminuser",
            password_hash=hash_password("adminpass123"),
            age=30,
            height=180,
            weight=80,
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def another_user():
    """Create another regular user and return it."""
    async with test_session_maker() as session:
        user = User(
            username="anotheruser",
            password_hash=hash_password("anotherpass123"),
            age=22,
            height=165,
            weight=60,
            role="user",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


# ==================== Authentication Tests ====================

class TestAuthenticationRequired:
    """Test that authentication is required for Settings endpoints."""

    async def test_get_me_requires_auth(self, client: AsyncClient):
        """GET /api/users/me should return 401 without auth."""
        response = await client.get("/api/users/me")
        assert response.status_code == 401

    async def test_get_me_requires_bearer_token(self, client: AsyncClient):
        """GET /api/users/me should return 401 with malformed auth header."""
        response = await client.get("/api/users/me", headers={"Authorization": "Invalid"})
        assert response.status_code == 401

    async def test_get_me_requires_valid_token(self, client: AsyncClient):
        """GET /api/users/me should return 401 with invalid token."""
        response = await client.get("/api/users/me", headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401

    async def test_update_me_requires_auth(self, client: AsyncClient):
        """PUT /api/users/me should return 401 without auth."""
        response = await client.put("/api/users/me", json={"username": "newname"})
        assert response.status_code == 401

    async def test_change_password_requires_auth(self, client: AsyncClient):
        """POST /api/users/change-password should return 401 without auth."""
        response = await client.post("/api/users/change-password", json={
            "current_password": "old",
            "new_password": "newpass123"
        })
        assert response.status_code == 401


# ==================== GET /api/users/me Tests ====================

class TestGetMe:
    """Test GET /api/users/me endpoint."""

    async def test_get_me_returns_user_profile(self, client: AsyncClient, regular_user: User):
        """GET /api/users/me should return the authenticated user's profile."""
        token = create_test_token(regular_user)
        response = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["age"] == 25
        assert data["height"] == 175
        assert data["weight"] == 70
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data

    async def test_get_me_does_not_return_password_hash(self, client: AsyncClient, regular_user: User):
        """GET /api/users/me should never return password_hash."""
        token = create_test_token(regular_user)
        response = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

    async def test_get_me_returns_only_own_profile(self, client: AsyncClient, regular_user: User, another_user: User):
        """GET /api/users/me should return only the authenticated user's data."""
        token = create_test_token(regular_user)
        response = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["username"] != "anotheruser"


# ==================== PUT /api/users/me Tests ====================

class TestUpdateMe:
    """Test PUT /api/users/me endpoint."""

    async def test_update_username(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should update username."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me", 
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "newusername"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"

    async def test_update_age(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should update age."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"age": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 30

    async def test_update_height(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should update height."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"height": 180}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["height"] == 180

    async def test_update_weight(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should update weight."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"weight": 75}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == 75

    async def test_update_multiple_fields(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should update multiple fields at once."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"age": 35, "height": 185, "weight": 85}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 35
        assert data["height"] == 185
        assert data["weight"] == 85

    async def test_username_uniqueness(self, client: AsyncClient, regular_user: User, another_user: User):
        """PUT /api/users/me should reject duplicate username."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "anotheruser"}
        )
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()

    async def test_username_uniqueness_allows_own_username(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should allow keeping the same username."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "testuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"

    async def test_role_cannot_be_changed_by_user(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should not allow a normal user to change their role."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "admin"}
        )
        # The update should succeed but role should remain unchanged
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"

    async def test_role_not_changed_in_database(self, client: AsyncClient, regular_user: User):
        """Verify role is not changed in the database after attempted update."""
        token = create_test_token(regular_user)
        await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "admin"}
        )
        # Fetch user again to verify role unchanged
        async with test_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == regular_user.id))
            user = result.scalar_one()
            assert user.role == "user"

    async def test_update_does_not_return_password_hash(self, client: AsyncClient, regular_user: User):
        """PUT /api/users/me should never return password_hash."""
        token = create_test_token(regular_user)
        response = await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"age": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

    async def test_update_other_user_isolation(self, client: AsyncClient, regular_user: User, another_user: User):
        """PUT /api/users/me should only update the authenticated user."""
        token = create_test_token(regular_user)
        await client.put("/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"username": "updateduser"}
        )
        # Verify another_user is unchanged
        async with test_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == another_user.id))
            user = result.scalar_one()
            assert user.username == "anotheruser"


# ==================== POST /api/users/change-password Tests ====================

class TestChangePassword:
    """Test POST /api/users/change-password endpoint."""

    async def test_change_password_correct_current(self, client: AsyncClient, regular_user: User):
        """POST /api/users/change-password should succeed with correct current password."""
        token = create_test_token(regular_user)
        response = await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "newpassword456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "password changed" in data["message"].lower()

    async def test_change_password_incorrect_current(self, client: AsyncClient, regular_user: User):
        """POST /api/users/change-password should fail with incorrect current password."""
        token = create_test_token(regular_user)
        response = await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "wrongpassword", "new_password": "newpassword456"}
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    async def test_new_password_stored_hashed(self, client: AsyncClient, regular_user: User):
        """New password should be stored as a bcrypt hash, not plaintext."""
        token = create_test_token(regular_user)
        await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "newpassword456"}
        )
        # Verify password is hashed in database
        async with test_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == regular_user.id))
            user = result.scalar_one()
            assert user.password_hash != "newpassword456"
            assert user.password_hash.startswith("$2b$")  # bcrypt hash prefix

    async def test_new_password_can_authenticate(self, client: AsyncClient, regular_user: User):
        """New password should be usable for login after change."""
        from app.services.auth_service import verify_password
        token = create_test_token(regular_user)
        await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "newpassword456"}
        )
        # Verify new password works
        async with test_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == regular_user.id))
            user = result.scalar_one()
            assert verify_password("newpassword456", user.password_hash)
            assert not verify_password("password123", user.password_hash)

    async def test_change_password_response_no_password(self, client: AsyncClient, regular_user: User):
        """Change password response should not contain password or hash."""
        token = create_test_token(regular_user)
        response = await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "newpassword456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "password" not in str(data).lower() or "changed" in str(data).lower()
        assert "hash" not in str(data).lower()

    async def test_change_password_min_length(self, client: AsyncClient, regular_user: User):
        """New password should enforce minimum length."""
        token = create_test_token(regular_user)
        response = await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "short"}
        )
        assert response.status_code == 422  # Validation error

    async def test_change_password_user_isolation(self, client: AsyncClient, regular_user: User, another_user: User):
        """Change password should only affect the authenticated user."""
        from app.services.auth_service import verify_password
        token = create_test_token(regular_user)
        await client.post("/api/users/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "password123", "new_password": "newpassword456"}
        )
        # Verify another_user's password is unchanged
        async with test_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.id == another_user.id))
            user = result.scalar_one()
            assert verify_password("anotherpass123", user.password_hash)
