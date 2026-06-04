from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """Hanya user dengan role seller yang bisa akses."""
    message = "Akses ditolak. Hanya seller yang diizinkan."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "seller"
        )


class IsBuyer(BasePermission):
    """Hanya user dengan role buyer yang bisa akses."""
    message = "Akses ditolak. Hanya buyer yang diizinkan."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "buyer"
        )