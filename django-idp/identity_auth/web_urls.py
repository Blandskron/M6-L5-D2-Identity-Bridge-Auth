from django.urls import path

from .web_views import HomeView, ResourceCreateView, ResourceListView, ResourcePublishView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),
    path("resources/new/", ResourceCreateView.as_view(), name="resource-create"),
    path("resources/<int:pk>/publish/", ResourcePublishView.as_view(), name="resource-publish"),
]
