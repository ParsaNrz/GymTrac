import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import Base, get_async_session
from app.models.user import User
from app.models.exercise import Exercise
from app.services.auth_service import hash_password, create_access_token
from tests.conftest import test_engine, test_session_maker, override_get_async_session


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
async def another_admin():
    """Create another admin user and return it."""
    async with test_session_maker() as session:
        user = User(
            username="anotheradmin",
            password_hash=hash_password("adminpass456"),
            age=35,
            height=170,
            weight=75,
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


@pytest_asyncio.fixture
async def sample_exercise():
    """Create a sample exercise and return it."""
    async with test_session_maker() as session:
        exercise = Exercise(
            name="Bench Press",
            primary_muscle_group="Chest",
            equipment="Barbell",
            description="A classic chest exercise",
        )
        session.add(exercise)
        await session.commit()
        await session.refresh(exercise)
        return exercise


# ==================== Admin Authorization Tests ====================

class TestAdminAuthorization:
    """Test that admin endpoints require admin role."""

    async def test_list_users_requires_auth(self, client: AsyncClient):
        """GET /api/admin/users should return 401 without auth."""
        response = await client.get("/api/admin/users")
        assert response.status_code == 401

    async def test_list_users_requires_admin_role(self, client: AsyncClient, regular_user: User):
        """GET /api/admin/users should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_get_user_requires_admin_role(self, client: AsyncClient, regular_user: User, another_user: User):
        """GET /api/admin/users/{id} should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.get(f"/api/admin/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_change_role_requires_admin_role(self, client: AsyncClient, regular_user: User, another_user: User):
        """PUT /api/admin/users/{id}/role should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.put(f"/api/admin/users/{another_user.id}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_delete_user_requires_admin_role(self, client: AsyncClient, regular_user: User, another_user: User):
        """DELETE /api/admin/users/{id} should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.delete(f"/api/admin/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_admin_list_exercises_requires_admin_role(self, client: AsyncClient, regular_user: User):
        """GET /api/admin/exercises should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.get("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_admin_create_exercise_requires_admin_role(self, client: AsyncClient, regular_user: User):
        """POST /api/admin/exercises should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Test Exercise",
            "primary_muscle_group": "Chest",
        })
        assert response.status_code == 403

    async def test_admin_update_exercise_requires_admin_role(self, client: AsyncClient, regular_user: User, sample_exercise: Exercise):
        """PUT /api/admin/exercises/{id} should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.put(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Updated Name",
        })
        assert response.status_code == 403

    async def test_admin_delete_exercise_requires_admin_role(self, client: AsyncClient, regular_user: User, sample_exercise: Exercise):
        """DELETE /api/admin/exercises/{id} should return 403 for normal users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.delete(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_admin_can_access_admin_endpoints(self, client: AsyncClient, admin_user: User):
        """GET /api/admin/users should return 200 for admin users."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200


# ==================== Admin User Management Tests ====================

class TestAdminUserManagement:
    """Test admin user management endpoints."""

    async def test_admin_list_users(self, client: AsyncClient, admin_user: User, regular_user: User, another_user: User):
        """Admin should be able to list all users."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # admin_user, regular_user, another_user
        usernames = {u["username"] for u in data}
        assert "adminuser" in usernames
        assert "testuser" in usernames
        assert "anotheruser" in usernames

    async def test_admin_list_users_no_password_hash(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Admin list users should never return password_hash."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        for user in data:
            assert "password_hash" not in user
            assert "password" not in user

    async def test_admin_get_user(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Admin should be able to get a specific user."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get(f"/api/admin/users/{regular_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "user"
        assert "password_hash" not in data

    async def test_admin_get_user_not_found(self, client: AsyncClient, admin_user: User):
        """Admin getting non-existent user should return 404."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users/99999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    async def test_admin_change_user_role_to_admin(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Admin should be able to promote a user to admin."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/users/{regular_user.id}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    async def test_admin_change_user_role_to_user(self, client: AsyncClient, admin_user: User, another_admin: User):
        """Admin should be able to demote an admin to user."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/users/{another_admin.id}/role?role=user", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"

    async def test_admin_change_user_role_invalid(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Admin changing to invalid role should return 400."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/users/{regular_user.id}/role?role=superadmin", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400

    async def test_admin_delete_user(self, client: AsyncClient, admin_user: User, another_user: User):
        """Admin should be able to delete a user."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.delete(f"/api/admin/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204

    async def test_admin_cannot_delete_self(self, client: AsyncClient, admin_user: User):
        """Admin should not be able to delete their own account."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.delete(f"/api/admin/users/{admin_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400

    async def test_admin_delete_user_not_found(self, client: AsyncClient, admin_user: User):
        """Admin deleting non-existent user should return 404."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.delete("/api/admin/users/99999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    async def test_admin_list_users_search(self, client: AsyncClient, admin_user: User, regular_user: User, another_user: User):
        """Admin should be able to search users by username."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users?search=test", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == "testuser"

    async def test_admin_list_users_pagination(self, client: AsyncClient, admin_user: User, regular_user: User, another_user: User):
        """Admin should be able to paginate users."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users?page=1&page_size=2", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


# ==================== Admin Exercise Management Tests ====================

class TestAdminExerciseManagement:
    """Test admin exercise management endpoints."""

    async def test_admin_list_exercises(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin should be able to list exercises."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Bench Press"

    async def test_admin_list_exercises_empty(self, client: AsyncClient, admin_user: User):
        """Admin should get empty list when no exercises exist."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    async def test_admin_create_exercise(self, client: AsyncClient, admin_user: User):
        """Admin should be able to create an exercise."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Squat",
            "primary_muscle_group": "Legs",
            "equipment": "Barbell",
            "description": "A classic leg exercise",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Squat"
        assert data["primary_muscle_group"] == "Legs"
        assert data["equipment"] == "Barbell"
        assert data["description"] == "A classic leg exercise"
        assert "id" in data

    async def test_admin_create_exercise_minimal(self, client: AsyncClient, admin_user: User):
        """Admin should be able to create an exercise with minimal fields."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Push Up",
            "primary_muscle_group": "Chest",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Push Up"
        assert data["primary_muscle_group"] == "Chest"
        assert data["equipment"] is None
        assert data["description"] is None

    async def test_admin_create_exercise_invalid_muscle_group(self, client: AsyncClient, admin_user: User):
        """Admin creating exercise with invalid muscle group should return 400."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Invalid Exercise",
            "primary_muscle_group": "InvalidGroup",
        })
        assert response.status_code == 400

    async def test_admin_create_exercise_missing_name(self, client: AsyncClient, admin_user: User):
        """Admin creating exercise without name should return 422."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "primary_muscle_group": "Chest",
        })
        assert response.status_code == 422

    async def test_admin_create_exercise_missing_muscle_group(self, client: AsyncClient, admin_user: User):
        """Admin creating exercise without muscle group should return 422."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Test Exercise",
        })
        assert response.status_code == 422

    async def test_admin_update_exercise(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin should be able to update an exercise."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Incline Bench Press",
            "equipment": "Dumbbell",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Incline Bench Press"
        assert data["equipment"] == "Dumbbell"
        assert data["primary_muscle_group"] == "Chest"  # unchanged

    async def test_admin_update_exercise_not_found(self, client: AsyncClient, admin_user: User):
        """Admin updating non-existent exercise should return 404."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put("/api/admin/exercises/99999", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Updated Name",
        })
        assert response.status_code == 404

    async def test_admin_update_exercise_invalid_muscle_group(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin updating exercise with invalid muscle group should return 400."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"}, json={
            "primary_muscle_group": "InvalidGroup",
        })
        assert response.status_code == 400

    async def test_admin_delete_exercise(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin should be able to delete an exercise."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.delete(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204

    async def test_admin_delete_exercise_not_found(self, client: AsyncClient, admin_user: User):
        """Admin deleting non-existent exercise should return 404."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.delete("/api/admin/exercises/99999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404

    async def test_admin_list_exercises_search(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin should be able to search exercises by name."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/exercises?search=bench", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Bench Press"

    async def test_admin_list_exercises_filter_muscle_group(self, client: AsyncClient, admin_user: User, sample_exercise: Exercise):
        """Admin should be able to filter exercises by muscle group."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/exercises?muscle_group=Chest", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["primary_muscle_group"] == "Chest"


# ==================== User Isolation Tests ====================

class TestUserIsolation:
    """Test that users cannot access or modify other users' data through admin endpoints."""

    async def test_user_cannot_list_other_users(self, client: AsyncClient, regular_user: User):
        """Normal user should not be able to list all users."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_user_cannot_view_other_user_details(self, client: AsyncClient, regular_user: User, another_user: User):
        """Normal user should not be able to view another user's details via admin."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.get(f"/api/admin/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_user_cannot_change_other_user_role(self, client: AsyncClient, regular_user: User, another_user: User):
        """Normal user should not be able to change another user's role."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.put(f"/api/admin/users/{another_user.id}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_user_cannot_delete_other_user(self, client: AsyncClient, regular_user: User, another_user: User):
        """Normal user should not be able to delete another user."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.delete(f"/api/admin/users/{another_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    async def test_user_cannot_create_exercise_via_admin(self, client: AsyncClient, regular_user: User):
        """Normal user should not be able to create exercises via admin endpoint."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.post("/api/admin/exercises", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Hacker Exercise",
            "primary_muscle_group": "Chest",
        })
        assert response.status_code == 403

    async def test_user_cannot_delete_exercise_via_admin(self, client: AsyncClient, regular_user: User, sample_exercise: Exercise):
        """Normal user should not be able to delete exercises via admin endpoint."""
        token = create_access_token(data={"sub": str(regular_user.id), "username": regular_user.username, "role": regular_user.role})
        response = await client.delete(f"/api/admin/exercises/{sample_exercise.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


# ==================== Password Hash Protection Tests ====================

class TestPasswordHashProtection:
    """Test that password_hash is never returned in any admin endpoint response."""

    async def test_list_users_no_password_hash(self, client: AsyncClient, admin_user: User, regular_user: User):
        """List users should not contain password_hash."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        for user in data:
            assert "password_hash" not in user
            assert "password" not in user

    async def test_get_user_no_password_hash(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Get user should not contain password_hash."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.get(f"/api/admin/users/{regular_user.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

    async def test_change_role_no_password_hash(self, client: AsyncClient, admin_user: User, regular_user: User):
        """Change role response should not contain password_hash."""
        token = create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role})
        response = await client.put(f"/api/admin/users/{regular_user.id}/role?role=admin", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data
