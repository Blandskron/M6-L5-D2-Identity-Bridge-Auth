# 🏗️ Architecture — Identity Platform

Este documento describe la **arquitectura técnica** del monorepo de identidad
basado en **Django (IdP)** + **FastAPI (Gateway)**, orquestado con Docker Compose.

---

## 1. Visión general

La plataforma sigue un modelo de **autoridad central de identidad**:

- **Django Identity Provider (IdP)**  
  Es la **fuente de verdad** para autenticación y sesión.
- **FastAPI Gateway**  
  Traduce sesión real → JWT estándar para microservicios.
- **PostgreSQL**  
  Persistencia del IdP.

El JWT **no es** la autoridad.  
La sesión Django **sí lo es**.

---

## 2. Diagrama lógico

```

Client (Web / App)
│
│ cookies (sessionid, csrftoken)
│ JWT (Authorization)
▼
FastAPI Gateway
│
│ HTTP interno (cookies reenviadas)
▼
Django Identity Provider
│
▼
PostgreSQL

```

---

## 3. Responsabilidades por servicio

### Django Identity Provider
- Autenticación real
- Creación y revocación de sesiones
- CSRF
- Exposición de identidad (`/me`)
- Gestión de grupos y permisos

No:
- JWT
- OAuth
- API pública de usuarios

---

### FastAPI Gateway
- Punto de entrada para clientes modernos
- Emisión de JWT RS256
- Refresh con doble validación
- Propagación de cookies
- Aislamiento del IdP del mundo exterior

No:
- Acceso directo a base de datos
- Lógica de autenticación propia

---

## 4. Comunicación entre servicios

- Red Docker compartida: `identity_net`
- DNS interno Docker:
  - `http://django-idp:8000`
- Protocolo: HTTP
- Cliente: `httpx.AsyncClient`

El gateway **siempre** valida sesión contra Django para:
- `/me`
- `/refresh`
- `/logout`

---

## 5. Flujo de refresh (clave)

1. Cliente envía `refresh_token` + cookies
2. Gateway valida JWT refresh
3. Gateway llama a Django `/me`
4. Django valida sesión real
5. Gateway compara `JWT.sub` vs `user.id`
6. Solo si coinciden → nuevos tokens

Esto garantiza:
- Logout real
- Revocación centralizada
- JWT no autónomos

---

## 6. Orquestación (Docker Compose)

- Postgres → Django → FastAPI
- Healthchecks reales
- Volúmenes persistentes
- Claves JWT montadas en modo read-only

---

## 7. Escalabilidad futura

Diseño preparado para:
- Redis (sesiones Django)
- Nginx / Traefik
- Public key para JWT
- Microservicios downstream

---

## 8. Principio rector

> **La sesión manda.  
El token obedece.**
