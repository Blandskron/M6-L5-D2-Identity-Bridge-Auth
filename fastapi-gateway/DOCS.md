# 📘 DOCS — FastAPI Gateway + Django IdP (Session Cookies → JWT)

Este documento explica **en detalle** cómo funciona el **FastAPI Gateway** que integra un **Django Identity Provider (IdP)** basado en **sesión/cookies + CSRF**, y cómo el gateway emite **JWT RS256** (access/refresh) para ser consumidos por otros servicios.

---

## 1) Contexto y objetivo

Este sistema está pensado para un escenario típico de arquitectura interna:

* **Django IdP** es la autoridad real de autenticación (credenciales, sesión, logout).
* **FastAPI Gateway** actúa como “traductor” y “puente”:

  * mantiene la **sesión real** vía cookies (sessionid/csrftoken)
  * genera **JWT access/refresh** para consumo estándar (Authorization: Bearer)
  * asegura que el refresh solo sea válido si la sesión real existe

### ¿Por qué hacer esto?

Porque muchas APIs/microservicios esperan JWT, pero tú quieres:

* centralizar sesión real (revocable) en el IdP
* evitar JWT “infinitos” en el ecosistema
* permitir logout real y control centralizado
* entregar identidad completa (roles/permisos) de forma consistente

---

## 2) Componentes y roles

### Django Identity Provider (IdP)

Responsable de:

* `POST /register/` crea usuario (y grupo base)
* `POST /login/` autentica y crea **sesión**
* `GET /me/` retorna identidad si sesión existe
* `POST /logout/` revoca sesión (`session.flush()`)
* `GET /csrf/` entrega CSRF token (para flows basados en cookie)

### FastAPI Gateway

Responsable de:

* consumir endpoints del IdP (httpx)
* propagar cookies relevantes al cliente (sessionid/csrftoken)
* construir y firmar JWT RS256
* implementar refresh con doble validación:

  * validar JWT refresh
  * validar sesión real contra Django `/me`

---

## 3) Flujo de autenticación

### 3.1 Registro (Gateway)

1. Cliente llama `POST /api/v1/register`
2. Gateway llama `POST Django /api/auth/register/`
3. Django:

   * crea usuario
   * asigna grupo `"user"`
4. Gateway:

   * recibe payload de identidad del usuario
   * genera `access_token` + `refresh_token`
   * reenvía cookies (si Django las setea)
5. Cliente recibe tokens + cookies

> Aunque Django registro no necesariamente crea sesión, tu gateway está preparado para reflejar cookies si existen.

---

### 3.2 Login (Gateway)

1. Cliente llama `POST /api/v1/login`
2. Gateway llama `POST Django /api/auth/login/`
3. Django:

   * valida credenciales
   * crea sesión y setea cookie `sessionid`
   * retorna `{ user, session_active: True }`
4. Gateway:

   * extrae `user`
   * firma JWT access/refresh usando RS256
   * setea cookies `sessionid` y `csrftoken` al cliente
5. Cliente queda autenticado:

   * por cookie (sesión real IdP)
   * por JWT (para APIs downstream)

---

### 3.3 Me (Identidad)

1. Cliente llama `GET /api/v1/me`
2. Gateway reenvía cookies recibidas (`request.cookies`) al Django IdP
3. Django valida sesión y retorna payload de identidad
4. Gateway responde con identidad

📌 Esto hace que `/me` sea el “source of truth” de sesión activa.

---

### 3.4 Refresh (doble validación)

Este punto es la **clave de tu arquitectura**.

1. Cliente llama `POST /api/v1/refresh` con:

   * `refresh_token` (JWT)
   * cookies (sessionid) incluidas por el cliente automáticamente o manualmente
2. Gateway:

   * decodifica refresh token (`decode_refresh_token`)
   * extrae `sub` (user_id)
3. Gateway valida sesión real:

   * llama a Django `/me` reenviando cookies
   * si Django responde 401 → sesión no existe → refresh inválido
4. Gateway compara:

   * `user["id"]` (desde Django) con `sub` (desde JWT)
   * si no coincide → 401
5. Gateway genera nuevos tokens y los retorna

✅ Resultado: **refresh solo funciona si la sesión real en Django sigue activa**.

---

### 3.5 Logout

1. Cliente llama `POST /api/v1/logout`
2. Gateway reenvía cookies al Django IdP `/logout`
3. Django revoca sesión (`session.flush()`)
4. Gateway responde `{ logged_out: true }` y propaga cookies si Django las cambia

---

## 4) Endpoints del Gateway

Base: `/api/v1`

| Método | Endpoint    | Request          | Response               | Descripción                                 |
| ------ | ----------- | ---------------- | ---------------------- | ------------------------------------------- |
| GET    | `/csrf`     | —                | `CsrfResponseSchema`   | Obtiene CSRF desde Django y propaga cookies |
| POST   | `/register` | `RegisterSchema` | `TokenSchema`          | Registra en Django y entrega JWT            |
| POST   | `/login`    | `LoginSchema`    | `TokenSchema`          | Login en Django + JWT                       |
| GET    | `/me`       | —                | `IdentityUserSchema`   | Identidad según sesión real                 |
| POST   | `/refresh`  | `RefreshSchema`  | `TokenSchema`          | Refresh JWT + validación sesión Django      |
| POST   | `/logout`   | —                | `LogoutResponseSchema` | Logout en Django                            |

---

## 5) Cookies: propagación y comportamiento

El gateway aplica cookies en `_apply_cookies()`:

* `sessionid`: HttpOnly=True
* `csrftoken`: HttpOnly=False
* `samesite="lax"`

```py
for name in ("sessionid", "csrftoken"):
    response.set_cookie(
        key=name,
        value=cookies[name],
        httponly=(name == "sessionid"),
        samesite="lax",
    )
```

### Recomendaciones según entorno

* **DEV**: `samesite="lax"` es cómodo
* **PROD (HTTPS)**:

  * `secure=True`
  * considerar `samesite="none"` si hay cross-site real (frontend en otro dominio) **y** `secure=True`

---

## 6) JWT: diseño y claims

### Firma

* Algoritmo: `RS256`
* Se firma con private key:

  * `JWT_PRIVATE_KEY_PATH=/app/keys/jwt_private.pem`

### Claims base que tú incluyes

En `_build_tokens()`:

* `sub`: user.id (string)
* `username`
* `groups`: lista de nombres de grupos
* `permissions`: lista de codenames

Ejemplo conceptual:

```json
{
  "sub": "11",
  "iat": 1769286283,
  "exp": 1769287183,
  "iss": "fastapi-gateway",
  "aud": "clients",
  "username": "tity",
  "groups": ["user"],
  "permissions": ["view_x", "edit_y"]
}
```

### Expiración

* Access: `ACCESS_TOKEN_EXPIRE_MINUTES=15`
* Refresh: `REFRESH_TOKEN_EXPIRE_DAYS=7`

---

## 7) Repositorio IdP (httpx)

`IdpRepository` encapsula las llamadas a Django:

* `csrf()`
* `register()`
* `login()`
* `me()`
* `logout()`

Incluye manejo de errores de negocio:

* 409 usuario existe en register
* 401 credenciales inválidas en login
* 403 usuario inactivo
* 401 no autenticado en me/logout

Y extrae cookies:

```py
return {
  "sessionid": resp.cookies.get("sessionid"),
  "csrftoken": resp.cookies.get("csrftoken"),
}
```

---

## 8) Settings (config.py)

Se centraliza:

* URLs del IdP
* configuración JWT
* expiraciones

Todo via `.env` usando `pydantic-settings`.

---

## 9) Ejecución local (sin Docker)

1. Crear venv e instalar:

```bash
pip install -r requirements.txt
```

2. Tener archivo `.env` listo.

3. Asegurar que el archivo exista:

* `keys/jwt_private.pem`

4. Ejecutar:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 10) Docker

### Build

```bash
docker build -t fastapi-gateway .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env fastapi-gateway
```

---

## 11) Ejemplos de prueba con curl

### Login guardando cookies

```bash
curl -c cookies.txt -i -X POST http://127.0.0.1:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tity","password":"bastian1234"}'
```

### Me usando cookies

```bash
curl -b cookies.txt http://127.0.0.1:8000/api/v1/me
```

### Refresh usando cookies + refresh token

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/v1/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<PEGAR_REFRESH_TOKEN>"}'
```

### Logout

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/v1/logout
```

---

## 12) Consideraciones importantes (producción)

### 12.1 Decodificación con private key

Tu `decode_refresh_token()` actualmente usa private key para decodificar. Funciona, pero el patrón estándar es:

* firmar con **private**
* verificar con **public**

✅ Sugerencia a futuro:

* agregar `JWT_PUBLIC_KEY_PATH`
* exponer endpoint `GET /public-key` para microservicios downstream

### 12.2 CORS + Cookies

Si tu frontend está en otro dominio, necesitarás:

* `allow_origins=["https://tu-frontend"]`
* `allow_credentials=True`

y cookies con `Secure`.

### 12.3 Rate limiting

Protege `/login` contra brute-force (middleware o gateway/reverse proxy).

### 12.4 Observabilidad

Loggear eventos:

* login success/fail
* refresh invalid
* logout

---

## 13) Qué garantiza esta arquitectura

✅ Tokens JWT que sirven para microservicios
✅ Sesión real centralizada (revocable) en IdP
✅ Refresh solo si sesión existe
✅ Identidad consistente (roles/permisos)
✅ Logout real y centralizado

---

## 14) Roadmap sugerido (opcional)

* Endpoint `GET /api/v1/public-key`
* Verificación refresh con `public key`
* CORS configurable por env
* Cookies `secure=True` y SameSite según dominio
* Redis sessions del lado Django si escalas IdP
* Rate limiting y audit logs
