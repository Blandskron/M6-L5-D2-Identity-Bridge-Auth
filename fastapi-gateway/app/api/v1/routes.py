from fastapi import APIRouter, Response, Request
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    LoginSchema,
    RegisterSchema,
    RefreshSchema,
    TokenSchema,
    IdentityUserSchema,
    LogoutResponseSchema,
    CsrfResponseSchema,
)

router = APIRouter(prefix="/api/v1", tags=["Auth"])
service = AuthService()


@router.get("/csrf", response_model=CsrfResponseSchema)
async def csrf(response: Response):
    data, cookies = await service.csrf()
    _apply_cookies(response, cookies)
    return data


@router.post("/register", response_model=TokenSchema, status_code=201)
async def register(payload: RegisterSchema, response: Response):
    tokens, cookies = await service.register(
        username=payload.username,
        password=payload.password,
        email=payload.email,
    )
    _apply_cookies(response, cookies)
    return tokens


@router.post("/login", response_model=TokenSchema)
async def login(payload: LoginSchema, response: Response):
    tokens, cookies = await service.login(
        username=payload.username,
        password=payload.password,
    )
    _apply_cookies(response, cookies)
    return tokens


@router.get("/me", response_model=IdentityUserSchema)
async def me(request: Request):
    # Consulta Django /me usando cookies de sesión del cliente
    return await service.me(cookies=dict(request.cookies))


@router.post("/refresh", response_model=TokenSchema)
async def refresh(payload: RefreshSchema, request: Request):
    # Refresh: valida JWT refresh + valida sesión real en Django usando cookies
    return await service.refresh(
        refresh_token=payload.refresh_token,
        cookies=dict(request.cookies),
    )


@router.post("/logout", response_model=LogoutResponseSchema)
async def logout(request: Request, response: Response):
    data, cookies = await service.logout(cookies=dict(request.cookies))
    _apply_cookies(response, cookies)
    return data


def _apply_cookies(response: Response, cookies: dict | None):
    if not cookies:
        return

    for name in ("sessionid", "csrftoken"):
        if name in cookies and cookies[name] is not None:
            response.set_cookie(
                key=name,
                value=cookies[name],
                httponly=(name == "sessionid"),
                samesite="lax",
            )
