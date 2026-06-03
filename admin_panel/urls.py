from django.urls import path
from .views import AdminSellerApplicationListView, AdminSellerApplicationDetailView

urlpatterns = [
    path("admin/applications/",          AdminSellerApplicationListView.as_view(),  name="admin-applications"),
    path("admin/applications/<int:pk>/", AdminSellerApplicationDetailView.as_view(), name="admin-application-detail"),
]