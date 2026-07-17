from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea grupos educativos y asigna sus permisos de forma idempotente."

    def handle(self, *args, **options):
        permission_sets = {
            "Lectores": ["view_educationalresource"],
            "Editores": ["view_educationalresource", "add_educationalresource", "change_educationalresource"],
            "Publicadores": ["view_educationalresource", "publish_educationalresource"],
        }
        for group_name, codenames in permission_sets.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.filter(
                content_type__app_label="identity_auth", codename__in=codenames
            )
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"Grupo listo: {group_name}"))
