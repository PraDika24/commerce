from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError as JWTTokenError
from rest_framework import status

from .serializers import SocialLoginSerializer
from .services.social_auth import social_authenticate
from utils.response import success_response, error_response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiRequest
from .serializers import (
    SocialLoginSerializer,
    LinkSocialSerializer,
    RegisterSerializer,
    LoginSerializer,
    LogOutSerializer,
    UpdateProfileSerializer,
    )

from .services.provider import PROVIDERS
from django.db import IntegrityError, OperationalError
from .models import SocialAccount
# Create your views here.
# users/api/views.py

class SocialLoginAPIView(APIView):

    @extend_schema(
        request=SocialLoginSerializer,
        responses=SocialLoginSerializer
    )
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

        mode = request.query_params.get("mode", "login")

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
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "email": user.email,
                        "role": user.role
                    }
                },
                message=message,
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return error_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)


class LinkSocialAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LinkSocialSerializer,
        responses=LinkSocialSerializer
    )
    def post(self, request):
        serializer = LinkSocialSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

        try:
            provider_impl = PROVIDERS[provider]
            user_info = provider_impl.verify(token)

            uid = user_info["uid"]

            # 🔥 1. CEK: user sudah punya provider ini
            if SocialAccount.objects.filter(
                user=request.user,
                provider=provider
            ).exists():
                return error_response(
                    message=f"Akun {provider} sudah terhubung",
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 🔥 2. CEK: uid dipakai user lain
            existing = SocialAccount.objects.filter(
                provider=provider,
                provider_uid=uid
            ).first()

            if existing and existing.user != request.user:
                return error_response(
                    message="Akun sudah terhubung dengan user lain",
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 🔥 3. CREATE + HANDLE DB CONSTRAINT
            try:
                SocialAccount.objects.create(
                    user=request.user,
                    provider=provider,
                    provider_uid=uid
                )
            except IntegrityError:
                return error_response(
                    message="Akun sudah terhubung (duplicate)",
                    status=status.HTTP_400_BAD_REQUEST
                )

            return success_response(
                message=f"Berhasil menghubungkan akun {provider}",
                data={"provider": provider},
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return error_response(
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )


class UnlinkSocialAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            responses=None
            )
    
    def delete(self, request, provider):
        
        SUPPORTED_PROVIDERS = ['google', 'facebook']

        if provider not in SUPPORTED_PROVIDERS:
            return error_response(
                message= f"Provider tidak didukung. Pilih: {', '.join(SUPPORTED_PROVIDERS)}",
                status=status.HTTP_400_BAD_REQUEST

            )
        
        
        try:
            social = SocialAccount.objects.get(
                user=request.user,
                provider=provider
            )
        except SocialAccount.DoesNotExist:
            return error_response(
                message=f"Akun {provider} tidak ditemukan",
                status=status.HTTP_404_NOT_FOUND
            )
        except OperationalError:
            return error_response(
                message="Gangguan database, coba lagi nanti",
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # 🔥 hitung jumlah social account
        total_social = SocialAccount.objects.filter(user=request.user).count()

        # 🔥 cek apakah user punya password
        has_password = request.user.has_usable_password()

        # ❗ PROTEKSI AKUN TERAKHIR
        if total_social == 1 and not has_password:
            return error_response(
                message="Tidak bisa unlink akun terakhir. Tambahkan metode login lain terlebih dahulu.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔥 delete
        social.delete()

        return success_response(
            message=f"Akun {provider} berhasil dilepas"
        )
        

class RegisterAPIView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses=RegisterSerializer
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        return success_response(
            data={
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            message="Registrasi Berhasil",
            status=status.HTTP_201_CREATED
        )
    

class LoginAPIView(APIView):

    
    @extend_schema(
        request=LoginSerializer,
        responses=LoginSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "role": user.role
                }
            },
            message="Login Sukses",
            status=status.HTTP_200_OK
        )
    

class LogOutApiView(APIView):
    
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogOutSerializer,
        responses=LogOutSerializer
    )
    def post(self, request):

        serializer = LogOutSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Refresh Token Invalid",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh_token = serializer.validated_data['token']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(
                message="LogOut Berhasil",
                status=status.HTTP_200_OK
            )
        except (InvalidToken, TokenError, JWTTokenError):
            # Token tidak valid (signature salah, malformed, expired, dll)
            # Token expired TIDAK perlu di-blacklist karena sudah tidak valid
            # Tetap return success agar frontend tetap logout (hapus token lokal)
            # TAPI jangan bilang "token invalid" karena bisa dimanfaatkan attacker
            return success_response(
                message="Logout berhasil",
                status=status.HTTP_200_OK
            )
        except Exception:
            return error_response(
                message="Logout tidak tersedia, silakan hapus token secara manual",
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        
class UpdateProfileAPIView(APIView):

    permission_classes= [IsAuthenticated]
    @extend_schema(
        request=UpdateProfileSerializer,
        responses=UpdateProfileSerializer
    )
    def patch(self, request, format=None):
        serializer = UpdateProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )

        if not serializer.is_valid():
            return error_response(
                message="Invalid Validation",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()

        return success_response(
            data=serializer.data,
            message="Profil Berhasil Diperbarui",
            status=status.HTTP_200_OK
        )
        
