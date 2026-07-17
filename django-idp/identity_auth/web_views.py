from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import EducationalResourceForm
from .models import EducationalResource


class HomeView(TemplateView):
    template_name = "identity_auth/home.html"


class ResourceListView(LoginRequiredMixin, ListView):
    """LoginRequiredMixin impide consultar recursos sin sesión activa."""

    model = EducationalResource
    template_name = "identity_auth/resource_list.html"
    context_object_name = "resources"


class ResourceCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Solo usuarios con el permiso add pueden crear el recurso."""

    model = EducationalResource
    form_class = EducationalResourceForm
    template_name = "identity_auth/resource_form.html"
    permission_required = "identity_auth.add_educationalresource"
    raise_exception = True
    success_url = reverse_lazy("resource-list")
    success_message = "Recurso creado correctamente."

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ResourcePublishView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Demuestra un permiso personalizado aplicado a una acción concreta."""

    model = EducationalResource
    fields = ()
    template_name = "identity_auth/resource_publish.html"
    permission_required = "identity_auth.publish_educationalresource"
    raise_exception = True
    success_url = reverse_lazy("resource-list")
    success_message = "Recurso publicado correctamente."

    def form_valid(self, form):
        form.instance.is_published = True
        return super().form_valid(form)
