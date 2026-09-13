from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    age = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)  # cm
    weight = Column(Integer, nullable=True)  # kg
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
    )
