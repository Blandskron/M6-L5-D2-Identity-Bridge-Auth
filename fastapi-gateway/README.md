# 🚪 FastAPI Gateway (Django IdP + Session Cookies → JWT)

Gateway de autenticación construido con **FastAPI** que delega la autenticación real a un **Django Identity Provider (IdP)** basado en **sesión + cookies + CSRF**, y luego emite **JWT (RS256)** para que otros servicios consuman un **token estándar** (Authorization: Bearer) sin perder el control real de sesión.

✅ **Django IdP valida credenciales y mantiene la sesión real (cookie `sessionid`)**
✅ **FastAPI emite `access_token` y `refresh_token`**
✅ **Refresh exige 2 validaciones**: JWT refresh **y** sesión real activa en Django (`/me`)
✅ **Logout revoca sesión en Django y limpia cookies**
✅ Arquitectura simple: `routes → service → repository → idp`

---

## 🎯 Objetivo

Este gateway existe para escenarios donde:

* quieres mantener un **IdP central con cookies/sesión** (Django)
* pero necesitas que microservicios consuman un **JWT estándar**
* sin convertir JWT en “la autoridad real” (la autoridad real sigue siendo Django, vía sesión)

📌 Resultado:

* el cliente (web/app) mantiene cookies (`sessionid`, `csrftoken`)
* el gateway emite tokens para APIs downstream
* el refresh solo funciona si la sesión real en Django sigue viva

---

## 🧩 Stack

* **Python 3.12**
* **FastAPI**
* **httpx** (cliente async)
* **python-jose** (JWT RS256)
* **pydantic v2** + **pydantic-settings**
* **Docker**

---

## 🔐 Modelo de seguridad

### 1) Login

1. Gateway recibe username/password
2. Llama a Django IdP `/api/auth/login/`
3. Django crea sesión y devuelve cookies (`sessionid`, `csrftoken`)
4. Gateway devuelve:

   * `access_token` (JWT)
   * `refresh_token` (JWT)
   * setea cookies en la respuesta (para mantener sesión real)

### 2) Me

* Gateway llama a Django IdP `/api/auth/me/` reenviando cookies del cliente.
* Devuelve identidad completa.

### 3) Refresh (doble validación)

* Gateway **decodifica el refresh token**
* Luego valida que la sesión real **sigue activa** llamando a Django `/me`
* Si el `user.id` no coincide con `sub` del refresh → 401

### 4) Logout

* Gateway llama a Django `/logout` con cookies del cliente
* Django revoca sesión
* Gateway refleja cookies en respuesta

---

## 📌 Endpoints (Gateway)

Base: `/api/v1`

| Método | Endpoint    | Respuesta              | Descripción                                 |
| ------ | ----------- | ---------------------- | ------------------------------------------- |
| GET    | `/csrf`     | `CsrfResponseSchema`   | Obtiene CSRF desde Django y propaga cookies |
| POST   | `/register` | `TokenSchema`          | Registra usuario en Django y retorna JWT    |
| POST   | `/login`    | `TokenSchema`          | Login vía Django + retorna JWT              |
| GET    | `/me`       | `IdentityUserSchema`   | Identidad según sesión real Django          |
| POST   | `/refresh`  | `TokenSchema`          | Refresh JWT + validación sesión real Django |
| POST   | `/logout`   | `LogoutResponseSchema` | Logout en Django + propagación cookies      |

---

## 👤 Payload de identidad

`GET /api/v1/me` retorna el árbol de identidad proveniente del Django IdP:

```json
{
  "id": 1,
  "username": "bastian",
  "email": "bastian@email.com",
  "is_active": true,
  "groups": [
    { "name": "user", "permissions": [{ "codename": "view_x", "name": "Can view X" }] }
  ],
  "permissions": [{ "codename": "edit_y", "name": "Can edit Y" }]
}
```

---

## 🧠 Arquitectura (carpetas)

Estructura lógica (según tus imports):

```
app/
  api/v1/routes.py           # Router FastAPI /api/v1
  services/auth_service.py   # Orquestación: tokens + validación sesión
  repositories/idp_repository.py  # Cliente HTTP hacia Django IdP
  core/config.py             # Settings por .env
  core/security.py           # JWT RS256: create/decode tokens
  schemas/auth_schema.py     # Pydantic schemas (request/response)
  main.py                    # FastAPI app
keys/
  jwt_private.pem            # clave privada RS256 (montada en /app/keys)
requirements.txt
Dockerfile
.env
```

---

## ⚙️ Variables de entorno (.env)

Ejemplo:

```env
# =========================
# DJANGO IDP BASE
# =========================
DJANGO_BASE_URL=http://django-idp:8000
DJANGO_CSRF_URL=/api/auth/csrf/
DJANGO_REGISTER_URL=/api/auth/register/
DJANGO_LOGIN_URL=/api/auth/login/
DJANGO_ME_URL=/api/auth/me/
DJANGO_LOGOUT_URL=/api/auth/logout/

# =========================
# JWT
# =========================
JWT_PRIVATE_KEY_PATH=/app/keys/jwt_private.pem
JWT_ALGORITHM=RS256
JWT_ISSUER=fastapi-gateway
JWT_AUDIENCE=clients

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🔑 Claves JWT (RS256)

Este gateway firma JWT con **clave privada**:

* `keys/jwt_private.pem` (requerida)
* el *ideal* en producción: generar también `jwt_public.pem` para validación en otros servicios.

📌 Nota: tu `decode_refresh_token()` usa private key para decodificar.
Funciona, pero en un diseño típico:

* **firmas con private**
* **verificas con public**

---

## 🐳 Docker

### Build

```bash
docker build -t fastapi-gateway .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env fastapi-gateway
```

Queda en:

```
http://localhost:8000
```

---

## ✅ Ejemplos de uso

### 1) Register

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"tity","password":"bastian1234","email":"tity@gmail.com"}'
```

🔸 Respuesta: `access_token`, `refresh_token` + cookies `sessionid`/`csrftoken`.

---

### 2) Login

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tity","password":"bastian1234"}'
```

---

### 3) Me (requiere cookies)

Primero guarda cookies del login:

```bash
curl -c cookies.txt -i -X POST http://127.0.0.1:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"tity","password":"bastian1234"}'
```

Luego:

```bash
curl -b cookies.txt http://127.0.0.1:8000/api/v1/me
```

---

### 4) Refresh (JWT + sesión real)

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/v1/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<PEGAR_REFRESH_TOKEN>"}'
```

Si la sesión en Django expiró o fue revocada → `401`.

---

### 5) Logout

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/v1/logout
```

---

## 🍪 Cookies propagadas

El gateway copia desde Django (si vienen) estas cookies:

* `sessionid` (HttpOnly)
* `csrftoken` (no HttpOnly)

```py
for name in ("sessionid", "csrftoken"):
  response.set_cookie(
    key=name,
    value=cookies[name],
    httponly=(name == "sessionid"),
    samesite="lax",
  )
```

📌 Recomendación típica para prod:

* `secure=True` bajo HTTPS
* `domain=...` si compartes cookies entre subdominios

---

## 🚫 Limitaciones actuales (intencionales / MVP)

* No incluye CORS en `main.py` (útil si frontend está en otro dominio)
* No expone public key endpoint (para validar JWT desde otros servicios)
* No gestiona “rotación” de refresh tokens (opcional futuro)
* No incluye rate limit / anti-bruteforce (recomendado en prod)

---

## 🛣️ Próximos pasos recomendados (opcionales)

1. Public key para microservicios:

* `GET /api/v1/public-key` → entrega `jwt_public.pem`

2. CORS configurable:

* permitir dominios por env + `allow_credentials=True`

3. Seguridad cookies:

* `secure=True` + SameSite según tu flujo real

4. Observabilidad:

* logs estructurados de auth, refresh, logout

---

## 📜 Licencia

Proyecto interno / educativo.
Uso libre en arquitecturas privadas.
