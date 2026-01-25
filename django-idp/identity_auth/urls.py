from django.urls import path
from .views import csrf_view, login_view, logout_view, register_view, me_view

urlpatterns = [
    path("csrf/", csrf_view),
    path("register/", register_view),
    path("login/", login_view),
    path("me/", me_view),
    path("logout/", logout_view),
]
