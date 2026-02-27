"""Esquemas Pydantic de request/response para endpoints de autenticación."""

from pydantic import BaseModel, EmailStr
from typing import Any, List


class LoginSchema(BaseModel):
    """Payload para login federado."""

    username: str
    password: str


class RegisterSchema(BaseModel):
    """Payload de registro en el IdP."""

    username: str
    password: str
    email: EmailStr


class RefreshSchema(BaseModel):
    """Payload para solicitar reemisión de tokens."""

    refresh_token: str


class TokenSchema(BaseModel):
    """Respuesta estándar de tokens del gateway."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class IdentityUserSchema(BaseModel):
    """Representación de identidad proveniente del IdP."""

    id: int
    username: str
    email: str
    is_active: bool
    groups: List[Any]
    permissions: List[Any]


class LogoutResponseSchema(BaseModel):
    """Respuesta de cierre de sesión."""

    logged_out: bool


class CsrfResponseSchema(BaseModel):
    """Respuesta del endpoint CSRF."""

    csrfToken: str
