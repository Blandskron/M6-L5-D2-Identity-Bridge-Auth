from django.contrib.auth.models import User


def _identity_payload(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email or "",
        "is_active": user.is_active,
        "groups": [
            {
                "name": g.name,
                "permissions": list(g.permissions.values("codename", "name")),
            }
            for g in user.groups.all()
        ],
        "permissions": list(user.user_permissions.values("codename", "name")),
    }
