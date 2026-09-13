from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import hash_password


async def seed_admin() -> None:
    """Create the initial admin user if one does not already exist.

    This runs on every application startup but is idempotent —
    it checks whether an admin user exists before creating one.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.role == "admin")
        result = await session.execute(stmt)
        existing_admin = result.scalar_one_or_none()

        if existing_admin is None:
            admin = User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
            session.add(admin)
            await session.commit()
