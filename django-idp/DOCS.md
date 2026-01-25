# 🆔 Django Identity Provider (Session-based) — Documentación técnica y de integración

Servicio interno de **Identity Provider (IdP)** construido con **Django + Django REST Framework**, orientado a **autenticación basada en sesión (cookies) + CSRF**, **sin JWT**.

Este IdP está diseñado para funcionar como **autoridad de identidad** dentro de una arquitectura con frontends web y/o otros microservicios (FastAPI, Django, Gateways, etc.) que delegan autenticación y obtienen el **payload de identidad** desde aquí.

---

## 1) ¿Qué problema resuelve?

En microservicios y aplicaciones web es común necesitar:

* Login/Logout centralizado (un solo lugar)
* Sesión válida y revocable sin tokens distribuidos
* Identidad consistente (usuario, roles, permisos)
* Control CSRF cuando se usan cookies
* Un servicio simple de identidad para consumir desde:

  * Frontend (React/Vue/Angular)
  * Backend API (FastAPI / Django / Gateways)
  * Middleware de autorización

Este IdP resuelve eso con un enfoque **clásico**:

✅ **Cookies + Sesión**
✅ **CSRF**
✅ **/me** para recuperar identidad
✅ **Grupos + permisos** en un árbol completo
❌ **Sin JWT** (por diseño)

---

## 2) Filosofía del proyecto (decisiones intencionales)

Este servicio **no es** un “Auth server público”. Es un IdP **interno**.

### Lo que sí hace

* Registro simple
* Login basado en sesión
* CSRF token para integraciones
* Entrega payload de identidad (roles/permisos)
* Logout (revoca la sesión)

### Lo que NO hace (intencional)

* ❌ JWT / Refresh tokens
* ❌ OAuth2 / OpenID Connect
* ❌ CRUD de usuarios por API
* ❌ Manejo complejo de sesiones (Redis, multi-tenant, etc.) — opcional futuro
* ❌ “Autorización por middleware” en DRF (en este MVP está abierto por configuración)

---

## 3) Arquitectura general

### Componentes

* `identity_auth`: endpoints de autenticación + serializadores
* `identity_docs`: documentación OpenAPI vía drf-spectacular
* `project`: settings y routing

### Flujo base

1. Cliente obtiene CSRF (si corresponde)
2. Cliente hace login (POST `/login/`)
3. Django crea cookie de sesión (`sessionid`)
4. Cliente consulta `/me/` para obtener identidad
5. Cliente usa identidad para autorización en frontend o en otros servicios
6. Logout revoca sesión con `request.session.flush()`

---

## 4) Endpoints expuestos

Todos los endpoints de auth están bajo:

`/api/auth/`

| Método | Endpoint     | Descripción                                              |
| ------ | ------------ | -------------------------------------------------------- |
| GET    | `/csrf/`     | entrega CSRF token (y permite setear cookie `csrftoken`) |
| POST   | `/register/` | crea usuario y lo asigna al grupo base `user`            |
| POST   | `/login/`    | autentica y crea sesión (cookie)                         |
| GET    | `/me/`       | devuelve identidad si la sesión está activa              |
| POST   | `/logout/`   | revoca sesión (flush)                                    |

> No existe `/refresh` por diseño: **no se usan tokens**.

---

## 5) Modelo de autenticación (cómo funciona)

### Login (Session-based)

En `login_view`:

* Valida `username` + `password`
* Usa `authenticate()`
* Verifica `is_active`
* Si está ok:

  * guarda `request.session["user_id"] = user.id`
  * responde identidad + `session_active = True`

Esto significa:

* La sesión real está soportada por cookie `sessionid` de Django
* El `user_id` guardado en la sesión es el “marcador” de autenticación interna

### Me (identidad según sesión)

En `me_view`:

* lee `request.session.get("user_id")`
* si no existe → `401 No autenticado`
* si existe → busca el usuario y retorna payload de identidad

### Logout

En `logout_view`:

* `request.session.flush()` elimina por completo la sesión

---

## 6) CSRF (por qué existe este endpoint)

El endpoint `/csrf/` usa:

```py
token = get_token(request)
```

Eso:

* genera un token CSRF válido
* permite que Django prepare la cookie `csrftoken` (dependiendo de config y contexto)
* sirve para integraciones donde:

  * frontend usa cookies
  * y los POST/PUT/DELETE requieren header `X-CSRFToken`

📌 Importante:

* Si tu cliente usa `fetch/axios` con cookies:

  * debes enviar `credentials: "include"` (en fetch)
  * o `withCredentials: true` (en axios)

---

## 7) Payload de identidad (contrato)

Este IdP entrega un payload completo con:

* info base del usuario
* grupos (roles) con permisos asociados
* permisos directos del usuario

Ejemplo:

```json
{
  "id": 1,
  "username": "bastian",
  "email": "bastian@email.com",
  "is_active": true,
  "groups": [
    {
      "name": "user",
      "permissions": [
        { "codename": "view_x", "name": "Can view X" }
      ]
    }
  ],
  "permissions": [
    { "codename": "edit_y", "name": "Can edit Y" }
  ]
}
```

### ¿Por qué entregar el árbol completo?

Porque permite que:

* frontend o gateway **autoricen** sin múltiples llamadas
* FastAPI o otros servicios puedan decidir:

  * “¿puede hacer X?”
  * “¿tiene role admin?”
* evita múltiples endpoints tipo `/roles`, `/permissions`, etc.

---

## 8) Documentación OpenAPI (Swagger / ReDoc)

Rutas:

* `/api/schema/`
* `/api/swagger/`
* `/api/redoc/`

Generadas con `drf-spectacular` y decoradores `@extend_schema`.

Incluye:

* Request serializers
* Response serializers
* Resúmenes por endpoint

---

## 9) Configuración del proyecto

### Settings relevantes

#### DRF sin auth por defecto (MVP)

```py
REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": [],
  "DEFAULT_PERMISSION_CLASSES": [],
}
```

Eso significa que **no se aplica autenticación automática DRF** (está “abierto”), y el control se hace manual en views.

> Esto es válido para un IdP interno en etapa inicial, pero en entornos reales se recomienda endurecerlo (ver sección 14).

#### DB con fallback

* por env: `DB_ENGINE=postgres` → Postgres
* si no: SQLite por defecto

---

## 10) Variables de entorno (.env)

Ejemplo incluido:

```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,django-idp

DB_ENGINE=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=identity_db
POSTGRES_USER=identity_user
POSTGRES_PASSWORD=identity_pass
```

Notas:

* `DJANGO_ALLOWED_HOSTS` soporta múltiples hosts separados por coma
* `DB_ENGINE` controla si usa Postgres o SQLite

---

## 11) Docker (cómo se ejecuta)

### Dockerfile (qué hace)

* Usa `python:3.12-slim`
* instala dependencias, incluyendo `libpq-dev` para Postgres
* copia el proyecto a `/app`
* ejecuta `/app/entrypoint.sh`
* corre `runserver` por defecto

### Entrypoint (qué hace)

1. `python manage.py migrate`
2. opcional `makemigrations` si `DJANGO_MAKEMIGRATIONS=1`
3. `collectstatic` si `DJANGO_COLLECTSTATIC=1`
4. crea superuser si `DJANGO_CREATE_SUPERUSER=1`
5. arranca el comando final (runserver o gunicorn)

Variables útiles:

* `DJANGO_CREATE_SUPERUSER=1`
* `DJANGO_SUPERUSER_USERNAME=admin`
* `DJANGO_SUPERUSER_PASSWORD=admin1234`

---

## 12) Ejemplos de consumo

### A) Frontend web (Fetch)

**Login** (enviar cookies):

```js
await fetch("http://localhost:8000/api/auth/login/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({ username: "tity", password: "bastian1234" })
});
```

**Me**:

```js
const me = await fetch("http://localhost:8000/api/auth/me/", {
  method: "GET",
  credentials: "include"
}).then(r => r.json());
```

### B) Axios

```js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/auth",
  withCredentials: true
});

await api.post("/login/", { username: "tity", password: "bastian1234" });
const me = await api.get("/me/");
```

### C) Integración con otro backend (FastAPI / Gateway)

Patrón típico:

1. el gateway recibe request del cliente con cookie `sessionid`
2. reenvía esa cookie al IdP consultando `/me/`
3. si `200`, obtiene identidad y autoriza
4. si `401`, bloquea

---

## 13) Contratos (serializers)

Los serializers definen un contrato claro:

* `RegisterRequestSerializer`: `{ username, password, email? }`
* `LoginRequestSerializer`: `{ username, password }`
* `LoginResponseSerializer`: `{ user, session_active }`
* `LogoutResponseSerializer`: `{ logged_out }`
* `CsrfResponseSerializer`: `{ csrfToken }`

Esto es útil porque:

* Swagger muestra schemas precisos
* consumidores saben exactamente qué enviar/recibir

---

## 14) Recomendaciones para endurecer seguridad (cuando pases a prod)

Si este IdP pasa a un entorno real, normalmente se agregan:

1. **Cookie settings**

* `SESSION_COOKIE_SECURE=True` (solo HTTPS)
* `CSRF_COOKIE_SECURE=True`
* `SESSION_COOKIE_SAMESITE="Lax" | "Strict"`
* `CSRF_COOKIE_SAMESITE="Lax" | "Strict"`

2. **CORS y credenciales**

* configurar CORS permitiendo dominios reales
* `Access-Control-Allow-Credentials: true`

3. **Backend de sesiones**

* Redis para sesiones compartidas entre réplicas

4. **Rate limiting**

* evitar brute-force en `/login/`

5. **Auditoría**

* logs de intentos de login / logout

6. **DRF auth/permissions**

* mover de “manual” a “estándar” si quieres endpoints protegidos automáticamente

---

## 15) Guía rápida de prueba manual (curl)

⚠️ Curl con cookies requiere guardar/reenviar cookies.

### Login guardando cookie

```bash
curl -c cookies.txt -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tity","password":"bastian1234"}'
```

### Me usando cookie

```bash
curl -b cookies.txt http://127.0.0.1:8000/api/auth/me/
```

### Logout

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/auth/logout/
```

---

## 16) Roadmap sugerido (opcional)

Si quieres evolucionarlo sin cambiar el concepto:

* ✅ Agregar CORS configurable por env
* ✅ Redis sessions (si escalas)
* ✅ Rate limit en login
* ✅ Endpoint `/health/`
* ✅ Opcional: endpoint `GET /public-key` solo si en el futuro migras a JWT (hoy NO aplica)
* ✅ Roles más formales: `admin`, `staff`, `auditor`, etc.
