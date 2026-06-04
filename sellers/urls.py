from django.urls import path
from .views import SellerApplicationView, StorePublicDetailView, StoreView

urlpatterns = [
    path("seller/apply/", SellerApplicationView.as_view(), name="seller-apply"),
    path("seller/apply/",          SellerApplicationView.as_view(),  name="seller-apply"),
    path("seller/store/",          StoreView.as_view(),              name="seller-store"),
    path("stores/<slug:slug>/",    StorePublicDetailView.as_view(),  name="store-detail"),
]

