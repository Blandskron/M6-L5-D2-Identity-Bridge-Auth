# 🧩 Identity Platform — Django IdP + FastAPI Gateway (Monorepo)

Plataforma de **identidad y autenticación** compuesta por múltiples servicios orquestados con **Docker Compose**, diseñada para arquitecturas modernas con:

* **Sesión real centralizada (cookies + CSRF)**
* **JWT estándar para microservicios**
* **Logout y refresh con validación fuerte**
* **Separación clara de responsabilidades**

Este repositorio sigue un enfoque **monorepo**, donde cada servicio es independiente pero coordinado.

---

## 🏗️ Arquitectura general

```
┌──────────────┐
│   Frontend   │
│ (Web / App)  │
└──────┬───────┘
       │ cookies + JWT
       ▼
┌────────────────────┐
│ FastAPI Gateway    │
│  (Auth Gateway)    │
│  - Emite JWT       │
│  - Valida sesión   │
└──────┬─────────────┘
       │ HTTP interno (cookies)
       ▼
┌────────────────────┐
│ Django Identity    │
│ Provider (IdP)     │
│  - Sesión real     │
│  - CSRF            │
│  - Roles/Permisos  │
└──────┬─────────────┘
       │
       ▼
┌────────────────────┐
│ PostgreSQL         │
│ (Identity DB)      │
└────────────────────┘
```

---

## 📦 Servicios del monorepo

### 1️⃣ PostgreSQL (`identity-postgres`)

Base de datos persistente para el **Django Identity Provider**.

* Imagen: `postgres:16-alpine`
* Volumen persistente: `pgdata`
* Healthcheck con `pg_isready`
* Red interna: `identity_net`

No es accesible directamente desde el host.

---

### 2️⃣ Django Identity Provider (`django-idp`)

Servicio **core de identidad**.
Es la **autoridad real de autenticación**.

Responsabilidades:

* Registro de usuarios
* Login basado en sesión (cookies)
* CSRF token
* Exposición de identidad (`/me`)
* Logout (revocación real de sesión)
* Gestión de grupos y permisos

Características clave:

* **No usa JWT**
* Autenticación basada en **Django sessions**
* Ideal para entornos web y corporativos
* Documentado con Swagger / ReDoc

Puertos:

* `8000:8000`

Healthcheck:

* `GET /api/schema/`

---

### 3️⃣ FastAPI Gateway (`fastapi-gateway`)

Servicio de **gateway de autenticación**.

No autentica usuarios directamente, sino que:

* Delegada autenticación al Django IdP
* Traduce sesión → JWT
* Protege el refresh con doble validación
* Sirve como punto de entrada para APIs modernas

Responsabilidades:

* `/login`, `/register`, `/logout`
* Emisión de `access_token` y `refresh_token`
* Validación de sesión real vía Django `/me`
* Propagación de cookies (`sessionid`, `csrftoken`)

Puertos:

* `8001:8000`

Healthcheck:

* `GET /docs`

---

## 🔁 Comunicación entre Django y FastAPI (punto clave)

### 🔐 Principio fundamental

> **Django es la autoridad real.
> FastAPI nunca confía solo en JWT.**

---

### 🧠 ¿Cómo se comunican?

* FastAPI **no accede a la base de datos**
* FastAPI **no mantiene estado de sesión**
* Toda validación de sesión se hace consultando a Django vía HTTP interno

Comunicación:

* Red Docker: `identity_net`
* URL interna: `http://django-idp:8000`
* Cliente HTTP: `httpx.AsyncClient`

---

### 🔄 Flujo real de login

1. Cliente → `POST /api/v1/login` (FastAPI)
2. FastAPI → `POST django-idp/api/auth/login/`
3. Django:

   * valida credenciales
   * crea sesión
   * devuelve cookie `sessionid`
4. FastAPI:

   * recibe identidad
   * genera JWT (access + refresh)
   * **reenvía cookies al cliente**
5. Cliente queda autenticado por:

   * sesión real (cookie)
   * JWT para APIs

---

### ♻️ Refresh con doble validación (clave del diseño)

Cuando el cliente llama `/refresh`:

1. FastAPI **decodifica el refresh token**
2. FastAPI llama a Django `/me` usando cookies del cliente
3. Django valida sesión real:

   * si no existe → 401
4. FastAPI compara:

   * `JWT.sub` vs `user.id` retornado por Django
5. Solo si ambos coinciden:

   * se emiten nuevos tokens

👉 **Si el usuario hizo logout en Django, el refresh deja de funcionar**
👉 **El JWT nunca es la fuente de verdad**

---

### 🚪 Logout real

1. Cliente → `/api/v1/logout` (FastAPI)
2. FastAPI → Django `/logout`
3. Django:

   * ejecuta `session.flush()`
4. FastAPI refleja cookies
5. Sesión revocada para todo el sistema

---


## 📚 Documentación adicional

Además de los README por servicio, se agregó un análisis técnico consolidado para mantenimiento y evolución:

- `docs/REPO_ANALISIS_TECNICO.md`

## 🐳 Docker Compose (orquestación)

El archivo `docker-compose.yml` define:

* Red compartida: `identity_net`
* Orden correcto de arranque:

  * Postgres → Django → FastAPI
* Healthchecks reales (no solo puertos abiertos)
* Persistencia de datos
* Montaje seguro de claves JWT (read-only)

### Arranque completo

```bash
docker compose up --build
```

Servicios disponibles:

| Servicio        | URL                                                                      |
| --------------- | ------------------------------------------------------------------------ |
| Django IdP      | [http://localhost:8000](http://localhost:8000)                           |
| Django Swagger  | [http://localhost:8000/api/swagger/](http://localhost:8000/api/swagger/) |
| FastAPI Gateway | [http://localhost:8001](http://localhost:8001)                           |
| FastAPI Docs    | [http://localhost:8001/docs](http://localhost:8001/docs)                 |

---

## 🔑 Claves JWT

* El gateway usa **RS256**
* Clave privada montada como volumen:

  ```
  ../fastapi-gateway/keys → /app/keys (read-only)
  ```

Esto permite:

* rotar claves sin rebuild
* aislar secretos del código
* exponer clave pública a microservicios en el futuro

---

## 🧠 Por qué este diseño es sólido

✅ Logout real y centralizado
✅ Sesiones revocables
✅ JWT compatibles con cualquier API
✅ Refresh seguro
✅ Separación clara de responsabilidades
✅ Ideal para microservicios y gateways
✅ Fácil de extender (Redis, CORS, Nginx, etc.)

---

## 🚫 Qué NO hace este sistema (intencional)

* ❌ No es OAuth2 / OIDC
* ❌ No expone JWT como autoridad única
* ❌ No expone CRUD público de usuarios
* ❌ No acopla FastAPI a la base de datos

---

## 🛣️ Próximos pasos sugeridos

* Endpoint `/public-key` en gateway
* Redis como backend de sesiones Django
* CORS configurable por entorno
* Cookies `Secure` en HTTPS
* Rate limiting en login
* Gateway como API Gateway real (Nginx / Traefik)

---

## 📜 Licencia

Proyecto interno / educativo / corporativo.
Uso libre en arquitecturas privadas.
