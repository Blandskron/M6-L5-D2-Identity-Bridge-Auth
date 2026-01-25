from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DJANGO_BASE_URL: str = "http://127.0.0.1:8000"

    DJANGO_CSRF_URL: str = "/api/auth/csrf/"
    DJANGO_REGISTER_URL: str = "/api/auth/register/"
    DJANGO_LOGIN_URL: str = "/api/auth/login/"
    DJANGO_ME_URL: str = "/api/auth/me/"
    DJANGO_LOGOUT_URL: str = "/api/auth/logout/"

    # JWT (como ya tenías)
    JWT_PRIVATE_KEY_PATH: str = str(BASE_DIR / "keys" / "jwt_private.pem")
    JWT_ALGORITHM: str = "RS256"
    JWT_ISSUER: str = "fastapi-gateway"
    JWT_AUDIENCE: str = "clients"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
