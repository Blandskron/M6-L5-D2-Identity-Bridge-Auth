from django.conf import settings
from django.db import models


class EducationalResource(models.Model):
    """Recurso simple para demostrar autorización CRUD con Django Auth."""

    title = models.CharField("título", max_length=120)
    description = models.TextField("descripción")
    is_published = models.BooleanField("publicado", default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creado por",
        on_delete=models.CASCADE,
        related_name="educational_resources",
    )
    created_at = models.DateTimeField("creado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "recurso educativo"
        verbose_name_plural = "recursos educativos"
        permissions = [("publish_educationalresource", "Puede publicar recursos educativos")]

    def __str__(self):
        return self.title
