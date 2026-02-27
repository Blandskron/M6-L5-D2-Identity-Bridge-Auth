"""Capa de aplicación para orquestar IdP + emisión/verificación de JWT."""

import httpx
from fastapi import HTTPException
from app.repositories.idp_repository import IdpRepository
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)


class AuthService:
    """Servicio principal de autenticación del gateway."""

    def __init__(self):
        self.idp = IdpRepository()

    async def csrf(self) -> tuple[dict, dict]:
        """Recupera CSRF token del IdP."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            return await self.idp.csrf(client)

    async def register(self, username: str, password: str, email: str) -> tuple[dict, dict]:
        """Registra usuario en IdP y retorna JWT + cookies."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            user, cookies = await self.idp.register(client, username, password, email)

        tokens = self._build_tokens(user)
        return tokens, cookies

    async def login(self, username: str, password: str) -> tuple[dict, dict]:
        """Login federado: IdP autentica y gateway emite JWT."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            user, cookies = await self.idp.login(client, username, password)

        tokens = self._build_tokens(user)
        return tokens, cookies

    async def me(self, cookies: dict) -> dict:
        """Obtiene identidad real consultando sesión del IdP."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            return await self.idp.me(client, cookies=cookies)

    async def refresh(self, refresh_token: str, cookies: dict) -> dict:
        """Reemite tokens si el refresh JWT coincide con la sesión activa en IdP."""
        payload = decode_refresh_token(refresh_token)
        subject = payload.get("sub")

        if not subject:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        # Validación crítica: el JWT por sí solo no basta, se confirma sesión real.
        async with httpx.AsyncClient(follow_redirects=True) as client:
            user = await self.idp.me(client, cookies=cookies)

        if str(user["id"]) != str(subject):
            raise HTTPException(status_code=401, detail="Sesión no coincide con el refresh token")

        return self._build_tokens(user)

    async def logout(self, cookies: dict) -> tuple[dict, dict]:
        """Cierra sesión en IdP y retorna estado/cookies resultantes."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            return await self.idp.logout(client, cookies=cookies)

    def _build_tokens(self, user: dict) -> dict:
        """Construye payload estándar para access/refresh token."""
        subject = str(user["id"])

        claims = {
            "username": user.get("username"),
            "groups": [g["name"] for g in user.get("groups", [])],
            "permissions": [p["codename"] for p in user.get("permissions", [])],
        }

        return {
            "access_token": create_access_token(subject, claims),
            "refresh_token": create_refresh_token(subject, claims),
            "token_type": "bearer",
        }
