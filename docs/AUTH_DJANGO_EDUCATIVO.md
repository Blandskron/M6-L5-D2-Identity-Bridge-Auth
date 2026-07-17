# Autenticación y autorización con Django

## Modelo Auth y seguridad

Django incluye usuarios, contraseñas con hash, sesiones, grupos y permisos en `django.contrib.auth`. `AuthenticationMiddleware` asocia la sesión a `request.user`; CSRF protege formularios POST; los validadores revisan contraseñas y el ORM evita construir SQL manual. `login()` registra el usuario en la sesión y `logout()` la elimina. Las migraciones crean las tablas `auth_user`, `auth_group`, `auth_permission` y `django_session`.

El proyecto ofrece dos flujos integrados: las vistas API conservan la comunicación con el gateway y ahora usan `authenticate`, `login` y `logout`; las rutas `/accounts/login/` y `/accounts/logout/` usan `LoginView` y `LogoutView` oficiales. `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` y `LOGIN_URL` están definidos en `settings.py`.

## Autorización, permisos y grupos

Autenticar responde quién es el usuario; autorizar decide qué puede hacer. Django crea por modelo los permisos `add`, `change`, `delete` y `view`, almacenados en `auth_permission`. `EducationalResource` agrega `publish_educationalresource` para demostrar una acción específica. `user.has_perm("identity_auth.add_educationalresource")` considera tanto permisos directos como los heredados de grupos.

El comando idempotente `python manage.py setup_auth_demo` crea:

- `Lectores`: puede ver.
- `Editores`: puede ver, crear y modificar.
- `Publicadores`: puede ver y publicar.

Los usuarios, grupos y permisos pueden examinarse en `/admin/`. También puede revisarse la tabla con `python manage.py shell -c "from django.contrib.auth.models import Permission; print(Permission.objects.filter(content_type__app_label='identity_auth').values('codename','name'))"`.

## Mixins y accesos no autorizados

Un mixin es una clase reutilizable que agrega un comportamiento a una vista basada en clases. `ResourceListView` usa `LoginRequiredMixin`: un visitante es redirigido al login y conserva `next`. Las vistas de crear y publicar combinan `LoginRequiredMixin` con `PermissionRequiredMixin`; un usuario autenticado sin el permiso recibe HTTP 403 (`raise_exception = True`). Así se distingue claramente entre falta de sesión y falta de autorización.

## Demostración

1. Iniciar con `docker compose up --build` y abrir `http://localhost:8000/`.
2. Entrar con `admin` / `admin1234`; el superusuario posee todos los permisos.
3. Crear usuarios desde `/admin/auth/user/`, asignarlos a los grupos y repetir las acciones.
4. Cerrar sesión mediante el formulario POST del menú.
5. Ejecutar `python manage.py test identity_auth` para comprobar redirecciones, login/logout, HTTP 403 y concesión de permisos.
