from django.urls import path
from .views import SellerApplicationView

urlpatterns = [
    path("seller/apply/", SellerApplicationView.as_view(), name="seller-apply"),
]

