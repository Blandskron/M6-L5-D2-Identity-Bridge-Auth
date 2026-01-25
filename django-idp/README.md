# 🆔 Django Identity Provider (Session-based)

Servicio de **Identity Provider (IdP)** construido con **Django + Django REST Framework**, orientado a **autenticación por sesión y CSRF**, sin JWT.

Diseñado para integrarse con **frontends web** y **backends (FastAPI, Django, etc.)** que delegan autenticación y control de identidad en este servicio.

---

## 🎯 Objetivo del servicio

Este proyecto **NO es una API pública de usuarios**.
Es un **servicio de identidad interno** que se encarga de:

* Registro de usuarios
* Login basado en sesión
* Gestión de CSRF
* Exposición de identidad, roles y permisos
* Logout y revocación de sesión

👉 Ideal para arquitecturas donde:

* El frontend usa cookies
* Otros microservicios confían en la sesión validada
* No se quiere JWT ni tokens distribuidos

---

## 🧩 Stack tecnológico

* **Python 3.12**
* **Django 5.x**
* **Django REST Framework**
* **drf-spectacular** (OpenAPI / Swagger)
* **SQLite** (por defecto, fácilmente reemplazable)

---

## 🔐 Modelo de autenticación

* Autenticación **basada en sesión**
* CSRF habilitado
* No usa JWT
* No expone refresh tokens
* No expone endpoints innecesarios

---

## 📌 Endpoints disponibles

Todos los endpoints están bajo `/api/auth/`

| Método | Endpoint     | Descripción                       |
| ------ | ------------ | --------------------------------- |
| GET    | `/csrf/`     | Obtiene CSRF token y setea cookie |
| POST   | `/register/` | Registro de usuario               |
| POST   | `/login/`    | Login (crea sesión)               |
| GET    | `/me/`       | Identidad del usuario autenticado |
| POST   | `/logout/`   | Cierra sesión                     |

📌 **No existe `/refresh` por diseño**

---

## 👤 Payload de identidad

El servicio expone un **árbol de identidad completo**:

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

Este payload está pensado para ser consumido por:

* Frontend
* FastAPI
* Gateways
* Middleware de autorización

---

## 📄 Documentación API (Swagger)

Disponible automáticamente en:

```
/api/swagger/
/api/redoc/
/api/schema/
```

Swagger incluye:

* Requests
* Responses
* Esquemas
* Descripción funcional

---

## 🐳 Docker

### Build

```bash
docker build -t django-idp .
```

### Run

```bash
docker run -p 8000:8000 django-idp
```

Servicio disponible en:

```
http://localhost:8000
```

---

## ⚙️ Configuración relevante

* Sesiones Django estándar
* CSRF habilitado
* Sin autenticación por defecto en DRF
* Ideal para ejecutarse detrás de:

  * Nginx
  * Gateway
  * Reverse proxy

---

## 🚫 Qué NO hace este servicio

* ❌ No gestiona JWT
* ❌ No maneja OAuth
* ❌ No es un auth público
* ❌ No expone CRUD de usuarios
* ❌ No expone refresh tokens

Esto es **intencional**.

---

## 🧠 Casos de uso típicos

* Frontend React / Vue / Angular con cookies
* Backend FastAPI que consulta `/me`
* Microservicios que confían en sesión activa
* Entornos corporativos / educativos
* Arquitecturas sin JWT

---

## 🚀 Próximos pasos posibles

Opcionales, **no incluidos por defecto**:

* Gunicorn + Nginx
* CORS configurado
* SameSite / Secure cookies
* Backend de sesiones en Redis
* Base de datos PostgreSQL

---

## 📜 Licencia

Proyecto interno / educativo.
Uso libre en arquitecturas privadas.
