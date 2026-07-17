# Generated for the educational authentication and authorization example.
import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("auth", "0012_alter_user_first_name_max_length"), migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="EducationalResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120, verbose_name="título")),
                ("description", models.TextField(verbose_name="descripción")),
                ("is_published", models.BooleanField(default=False, verbose_name="publicado")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="creado")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="educational_resources", to=django.conf.settings.AUTH_USER_MODEL, verbose_name="creado por")),
            ],
            options={"verbose_name": "recurso educativo", "verbose_name_plural": "recursos educativos", "ordering": ["-created_at"], "permissions": [("publish_educationalresource", "Puede publicar recursos educativos")]},
        )
    ]
