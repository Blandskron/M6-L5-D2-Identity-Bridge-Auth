# 🔐 Security Model — Identity Platform

Este documento explica el **modelo de seguridad** del sistema de identidad
y las decisiones tomadas conscientemente.

---

## 1. Principio fundamental

> **Django es la autoridad real de autenticación.  
JWT nunca es la fuente de verdad.**

Esto evita:
- sesiones huérfanas
- refresh infinito
- JWT válidos después de logout

---

## 2. Autenticación

### Django IdP
- Autenticación basada en sesión
- Cookies:
  - `sessionid` (HttpOnly)
  - `csrftoken`
- CSRF habilitado

### FastAPI Gateway
- No autentica credenciales directamente
- Emite JWT solo después de validar Django

---

## 3. JWT

- Algoritmo: RS256
- Firmado por el gateway
- Claims mínimos:
  - `sub` (user id)
  - `username`
  - `groups`
  - `permissions`

JWT sirve para:
- APIs downstream
- autorización stateless

JWT **no sirve** para:
- validar login
- validar sesión activa sin Django

---

## 4. Refresh Token (doble validación)

Para emitir nuevos tokens se requiere:

1. Refresh JWT válido
2. Sesión Django activa
3. Coincidencia entre:
   - `JWT.sub`
   - `Django user.id`

Si cualquiera falla → `401`.

---

## 5. Logout

- El logout siempre ocurre en Django
- `session.flush()` revoca sesión
- El refresh deja de funcionar inmediatamente

---

## 6. Cookies

Configuración actual (DEV):

- `HttpOnly`: solo `sessionid`
- `SameSite`: `Lax`

Recomendado en PROD:
- `Secure: true`
- `SameSite: None` (si frontend en otro dominio)
- HTTPS obligatorio

---

## 7. CSRF

- Endpoint dedicado `/csrf`
- Compatible con:
  - fetch
  - axios
  - frontends con cookies

---

## 8. Ataques mitigados

- ❌ Refresh después de logout
- ❌ Token replay sin sesión
- ❌ JWT robado sin cookie
- ❌ Escalada por refresh autónomo

---

## 9. Recomendaciones adicionales (PROD)

- Rate limiting en `/login`
- Redis como backend de sesiones
- Logs de autenticación
- Rotación de claves JWT
- Endpoint de clave pública

---

## 10. Qué NO cubre este sistema

- OAuth2 / OIDC
- MFA
- Passwordless
- SSO externo

(Se pueden agregar, pero no forman parte del diseño base)
```
