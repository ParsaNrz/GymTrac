from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_expiration_minutes: int = 1440
    database_url: str = "sqlite+aiosqlite:///./data/gym_trac.db"
    admin_username: str = "admin"
    admin_password: str = "change-me-after-first-login"
    frontend_origin: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
