from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import EducationalResource


class AuthenticationAndAuthorizationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("student", password="safe-pass-123")

    def test_protected_list_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("resource-list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('resource-list')}")

    def test_builtin_login_and_logout_flow(self):
        response = self.client.post(reverse("login"), {"username": "student", "password": "safe-pass-123"})
        self.assertRedirects(response, reverse("resource-list"))
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_create_requires_permission(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("resource-create")).status_code, 403)
        self.user.user_permissions.add(Permission.objects.get(codename="add_educationalresource"))
        response = self.client.post(reverse("resource-create"), {"title": "Sesiones", "description": "Recurso de prueba"})
        self.assertRedirects(response, reverse("resource-list"))
        self.assertTrue(EducationalResource.objects.filter(title="Sesiones", created_by=self.user).exists())

    def test_publish_action_requires_custom_permission(self):
        resource = EducationalResource.objects.create(title="Permisos", description="Demo", created_by=self.user)
        self.client.force_login(self.user)
        url = reverse("resource-publish", args=[resource.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.user.user_permissions.add(Permission.objects.get(codename="publish_educationalresource"))
        self.assertRedirects(self.client.post(url), reverse("resource-list"))
        resource.refresh_from_db()
        self.assertTrue(resource.is_published)

    def test_api_login_uses_standard_django_session(self):
        response = self.client.post("/api/auth/login/", {"username": "student", "password": "safe-pass-123"}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.client.post("/api/auth/logout/")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
