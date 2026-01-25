from pydantic import BaseModel, EmailStr
from typing import Any, List


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(BaseModel):
    username: str
    password: str
    email: EmailStr


class RefreshSchema(BaseModel):
    refresh_token: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class IdentityUserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    groups: List[Any]
    permissions: List[Any]


class LogoutResponseSchema(BaseModel):
    logged_out: bool


class CsrfResponseSchema(BaseModel):
    csrfToken: str
