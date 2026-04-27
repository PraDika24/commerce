
from django.urls import path
from .views import (
    SocialLoginAPIView,
    LinkSocialAccountAPIView
)

urlpatterns = [
    path('auth/social/', SocialLoginAPIView.as_view()),
    path('link/', LinkSocialAccountAPIView.as_view())
]