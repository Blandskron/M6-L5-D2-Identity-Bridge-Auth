# 🤝 Contributing

Gracias por tu interés en contribuir a este proyecto.

Este repositorio sigue un enfoque **arquitectónico y educativo**, por lo que
las contribuciones deben respetar las decisiones de diseño existentes.

---

## 1. Filosofía del proyecto

Antes de contribuir, entiende estos principios:

- Django es la autoridad de identidad
- FastAPI es un gateway, no un IdP
- JWT no reemplaza la sesión
- Simplicidad > complejidad
- Seguridad explícita > magia

PRs que rompan estos principios probablemente serán rechazados.

---

## 2. Estructura del monorepo

```

/
├─ docker-compose.yml
├─ django-idp/
├─ fastapi-gateway/
├─ README.md
├─ DOCS.md
├─ ARCHITECTURE.md
├─ SECURITY.md
├─ CONTRIBUTING.md
└─ llms.txt

```

Cada servicio es **autónomo** y debe mantenerse desacoplado.

---

## 3. Reglas generales

- No acoplar FastAPI a la DB
- No mover lógica de sesión fuera de Django
- No introducir JWT como fuente de verdad
- Mantener código legible y explícito
- Evitar abstracciones innecesarias

---

## 4. Estilo de código

### Python
- PEP8
- Tipado explícito cuando aporte claridad
- Funciones pequeñas y con responsabilidad única

### FastAPI
- `routes → services → repositories`
- No lógica de negocio en routers

### Django
- Views simples
- Serializers claros
- Nada de “magia” innecesaria

---

## 5. Commits

Formato recomendado:

```

feat(gateway): validate refresh against django session
fix(idp): handle inactive user on login
docs: clarify security model

```

---

## 6. Pull Requests

Incluye siempre:
- qué problema resuelve
- por qué es necesario
- impacto en seguridad (si aplica)

Si el cambio afecta autenticación o refresh:
👉 documentarlo en `SECURITY.md`.

---

## 7. Testing (recomendado)

Antes de enviar PR:
- login → refresh → logout → refresh (debe fallar)
- sesión expirada → refresh (debe fallar)
- cookies ausentes → me / refresh (401)

---

## 8. Licencia

Al contribuir, aceptas que tu código se libere bajo la
licencia del proyecto (MIT).
```
