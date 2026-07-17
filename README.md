# Identity Bridge: autenticación y autorización con Django

Proyecto educativo que conserva la arquitectura original de Django IdP + FastAPI Gateway y añade una demostración web completa del modelo Auth de Django.

## Funcionalidades

- Registro, login, introspección y logout por API para el gateway.
- Login y logout web mediante las vistas oficiales de Django.
- Sesiones, CSRF, validadores de contraseña y panel de administración.
- Recurso educativo protegido con `LoginRequiredMixin`.
- Creación y publicación protegidas con `PermissionRequiredMixin`.
- Permisos básicos `add`, `change`, `delete`, `view` y permiso personalizado `publish`.
- Grupos `Lectores`, `Editores` y `Publicadores`, creados idempotentemente.
- SQLite persistente en Docker y pruebas automatizadas de autenticación/autorización.

La explicación conceptual y el guion de evaluación están en [docs/AUTH_DJANGO_EDUCATIVO.md](docs/AUTH_DJANGO_EDUCATIVO.md).

## Ejecución con Docker

```bash
docker compose up --build
```

Servicios:

- Aplicación Django: http://localhost:8000/
- Panel admin: http://localhost:8000/admin/
- Login: http://localhost:8000/accounts/login/
- Recursos protegidos: http://localhost:8000/resources/
- Swagger Django: http://localhost:8000/api/swagger/
- Gateway FastAPI: http://localhost:8001/docs

Credenciales educativas: `admin` / `admin1234`.

El `entrypoint.sh` ejecuta migraciones, configura grupos, crea el superusuario si no existe, recolecta estáticos e inicia el servidor. Puede ejecutarse repetidamente sin duplicar datos ni fallar.

Si los puertos están ocupados, pueden cambiarse sin editar archivos:

```bash
DJANGO_PORT=8010 GATEWAY_PORT=8011 docker compose up --build
```

En PowerShell:

```powershell
$env:DJANGO_PORT=8010
$env:GATEWAY_PORT=8011
docker compose up --build
```

## Verificación

Dentro del servicio Django:

```bash
docker compose run --rm django-idp python manage.py check
docker compose run --rm django-idp python manage.py migrate --noinput
docker compose run --rm django-idp python manage.py test
docker compose config
docker compose build
```

Sin Docker, instalar `django-idp/requirements.txt` y ejecutar los mismos comandos desde `django-idp/`.

## Estructura principal

- `django-idp/`: autoridad de identidad, aplicación web y API Django.
- `fastapi-gateway/`: gateway que delega autenticación en Django y emite JWT.
- `docs/AUTH_DJANGO_EDUCATIVO.md`: conceptos y demostración de la evaluación.
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `entrypoint.sh`: ejecución reproducible desde la raíz.
