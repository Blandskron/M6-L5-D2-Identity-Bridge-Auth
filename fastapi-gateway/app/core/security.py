"""Utilidades de seguridad: creación y validación de JWT para el gateway."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from jose import jwt, JWTError
from fastapi import HTTPException
from app.core.config import get_settings

settings = get_settings()


def _private_key() -> str:
    """Carga la clave privada usada para firmar tokens."""
    return Path(settings.JWT_PRIVATE_KEY_PATH).read_text()


def _create_token(subject: str, claims: dict, expires_delta: timedelta) -> str:
    """Construye un JWT firmado con claims base y claims de negocio."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        **claims,
    }
    return jwt.encode(payload, _private_key(), algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, claims: dict) -> str:
    """Genera access token de corta duración."""
    return _create_token(
        subject,
        claims,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, claims: dict) -> str:
    """Genera refresh token de larga duración."""
    return _create_token(
        subject,
        claims,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_refresh_token(token: str) -> dict:
    """Valida refresh token y devuelve su payload decodificado."""
    try:
        return jwt.decode(
            token,
            _private_key(),  # Nota: para RS256 idealmente verificar con public key.
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
