
from django.urls import path
from .views import (
    SocialLoginAPIView,
    LinkSocialAccountAPIView,
    UnlinkSocialAccountAPIView,
    RegisterAPIView,
    LoginAPIView,
    LogOutApiView,
    UpdateProfileAPIView,
    VerifyEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    ResendVerificationView,
    DeleteAccountView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/social/', SocialLoginAPIView.as_view()),
    path('link/', LinkSocialAccountAPIView.as_view()),
    path('unlink/<str:provider>/', UnlinkSocialAccountAPIView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/register/', RegisterAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/logout/', LogOutApiView.as_view()),
    path('profile/', UpdateProfileAPIView.as_view()),
    path('verify-email/', VerifyEmailView.as_view(), name="verify-email"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(),  name="forgot-password"),
    path("auth/reset-password/",  ResetPasswordView.as_view(),   name="reset-password"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/resend-verification/", ResendVerificationView.as_view(), name="resend-verification"),
    # urls.py
    path("auth/delete-account/", DeleteAccountView.as_view(), name="delete-account"),

]