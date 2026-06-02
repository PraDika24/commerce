from django.contrib.auth import get_user_model
from django.db import IntegrityError, OperationalError

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError as JWTTokenError

from drf_spectacular.utils import extend_schema

from .serializers import (
    SocialLoginSerializer,
    LinkSocialSerializer,
    RegisterSerializer,
    LoginSerializer,
    LogOutSerializer,
    UpdateProfileSerializer,
)
from .services.social_auth import social_authenticate
from .services.provider import PROVIDERS
from .models import SocialAccount
from .tokens import confirm_verification_token
from utils.response import success_response, error_response

User = get_user_model()


class SocialLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=SocialLoginSerializer)
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = serializer.validated_data["provider"]
        token    = serializer.validated_data["token"]

        try:
            user, created = social_authenticate(provider, token)
            refresh = RefreshToken.for_user(user)
            message = (
                f"Register dengan {provider} berhasil"
                if created else
                f"Login dengan {provider} berhasil"
            )
            return success_response(
                data={
                    "access":  str(refresh.access_token),
                    "refresh": str(refresh),
                    "user":    {"email": user.email, "role": user.role},
                },
                message=message,
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return error_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)


class LinkSocialAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LinkSocialSerializer)
    def post(self, request):
        serializer = LinkSocialSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = serializer.validated_data["provider"]
        token    = serializer.validated_data["token"]

        try:
            provider_impl = PROVIDERS[provider]
            user_info     = provider_impl.verify(token)
            uid           = user_info["uid"]

            if SocialAccount.objects.filter(user=request.user, provider=provider).exists():
                return error_response(
                    message=f"Akun {provider} sudah terhubung",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing = SocialAccount.objects.filter(provider=provider, provider_uid=uid).first()
            if existing and existing.user != request.user:
                return error_response(
                    message="Akun sudah terhubung dengan user lain",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                SocialAccount.objects.create(
                    user=request.user, provider=provider, provider_uid=uid
                )
            except IntegrityError:
                return error_response(
                    message="Akun sudah terhubung (duplicate)",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return success_response(
                message=f"Berhasil menghubungkan akun {provider}",
                data={"provider": provider},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return error_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)


class UnlinkSocialAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    SUPPORTED_PROVIDERS = ["google", "facebook"]

    def delete(self, request, provider):
        if provider not in self.SUPPORTED_PROVIDERS:
            return error_response(
                message=f"Provider tidak didukung. Pilih: {', '.join(self.SUPPORTED_PROVIDERS)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            social = SocialAccount.objects.get(user=request.user, provider=provider)
        except SocialAccount.DoesNotExist:
            return error_response(
                message=f"Akun {provider} tidak ditemukan",
                status=status.HTTP_404_NOT_FOUND,
            )
        except OperationalError:
            return error_response(
                message="Gangguan database, coba lagi nanti",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        total_social = SocialAccount.objects.filter(user=request.user).count()
        if total_social == 1 and not request.user.has_usable_password():
            return error_response(
                message="Tidak bisa unlink akun terakhir. Tambahkan metode login lain terlebih dahulu.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        social.delete()
        return success_response(message=f"Akun {provider} berhasil dilepas")


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        return success_response(
            data={
                "email":      user.email,
                "first_name": user.first_name,
                "last_name":  user.last_name,
            },
            message="Registrasi Berhasil",
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user    = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "access":  str(refresh.access_token),
                "refresh": str(refresh),
                "user":    {"email": user.email, "role": user.role},
            },
            message="Login Sukses",
            status=status.HTTP_200_OK,
        )


class LogOutApiView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LogOutSerializer)
    def post(self, request):
        serializer = LogOutSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Refresh Token Invalid",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh_token = serializer.validated_data["token"]
        try:
            RefreshToken(refresh_token).blacklist()
        except (InvalidToken, TokenError, JWTTokenError):
            pass  # Token expired/invalid — tetap logout di sisi client
        except Exception:
            return error_response(
                message="Logout tidak tersedia, silakan hapus token secara manual",
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        return success_response(message="Logout Berhasil", status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UpdateProfileSerializer)
    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                message="Invalid Validation",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return success_response(
            data=serializer.data,
            message="Profil Berhasil Diperbarui",
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return error_response(message="Token tidak ditemukan", status=status.HTTP_400_BAD_REQUEST)

        email = confirm_verification_token(token)
        if not email:
            return error_response(message="Token tidak valid atau sudah expired", status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return error_response(message="User tidak ditemukan", status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return success_response(message="Email sudah diverifikasi sebelumnya", status=status.HTTP_200_OK)

        user.is_active = True
        user.email_verified = True
        user.save(update_fields=["is_active", "email_verified"])
        return success_response(message="Email berhasil diverifikasi", data={"email": user.email}, status=status.HTTP_200_OK)