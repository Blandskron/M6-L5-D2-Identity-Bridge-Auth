import httpx
from fastapi import HTTPException
from app.core.config import get_settings


class IdpRepository:
    def __init__(self):
        self.settings = get_settings()

    def _url(self, path: str) -> str:
        return f"{self.settings.DJANGO_BASE_URL}{path}"

    @staticmethod
    def _extract_cookies(resp: httpx.Response) -> dict:
        return {
            "sessionid": resp.cookies.get("sessionid"),
            "csrftoken": resp.cookies.get("csrftoken"),
        }

    async def csrf(self, client: httpx.AsyncClient) -> tuple[dict, dict]:
        resp = await client.get(self._url(self.settings.DJANGO_CSRF_URL))
        resp.raise_for_status()
        return resp.json(), self._extract_cookies(resp)

    async def register(
        self,
        client: httpx.AsyncClient,
        username: str,
        password: str,
        email: str,
    ) -> tuple[dict, dict]:
        resp = await client.post(
            self._url(self.settings.DJANGO_REGISTER_URL),
            json={"username": username, "password": password, "email": email},
        )

        if resp.status_code == 409:
            raise HTTPException(status_code=409, detail="El usuario ya existe")

        resp.raise_for_status()
        return resp.json(), self._extract_cookies(resp)

    async def login(
        self,
        client: httpx.AsyncClient,
        username: str,
        password: str,
    ) -> tuple[dict, dict]:
        resp = await client.post(
            self._url(self.settings.DJANGO_LOGIN_URL),
            json={"username": username, "password": password},
        )

        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="Usuario inactivo")

        resp.raise_for_status()
        data = resp.json()

        if "user" not in data:
            raise HTTPException(status_code=500, detail="Respuesta inválida del Identity Provider")

        return data["user"], self._extract_cookies(resp)

    async def me(self, client: httpx.AsyncClient, cookies: dict) -> dict:
        resp = await client.get(self._url(self.settings.DJANGO_ME_URL), cookies=cookies)

        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="No autenticado")

        resp.raise_for_status()
        return resp.json()

    async def logout(self, client: httpx.AsyncClient, cookies: dict) -> tuple[dict, dict]:
        resp = await client.post(self._url(self.settings.DJANGO_LOGOUT_URL), cookies=cookies)

        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="No autenticado")

        resp.raise_for_status()
        return resp.json(), self._extract_cookies(resp)
