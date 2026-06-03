from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Hanya user dengan role admin atau is_staff yang bisa akses.
    """
    message = "Akses ditolak. Hanya admin yang diizinkan."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == "admin" or request.user.is_staff)
        )