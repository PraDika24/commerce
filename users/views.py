from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .serializers import SocialLoginSerializer
from .services.social_auth import social_authenticate
from utils.response import success_response, error_response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema
from .serializers import (
    SocialLoginSerializer,
    LinkSocialSerializer
    )

from .services.provider import PROVIDERS

from .models import SocialAccount
# Create your views here.
class SocialLoginAPIView(APIView):
    @extend_schema(
        request=SocialLoginSerializer,
        responses= SocialLoginSerializer
    )
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                "Validation error",
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

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
            return error_response(str(e), status=status.HTTP_400_BAD_REQUEST)


class LinkSocialAccountAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LinkSocialSerializer,
        responses=LinkSocialSerializer
    )
    def post(self, request, format=None):
        serializer = LinkSocialSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                error=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

        try:
            provider_impl = PROVIDERS[provider]
            user_info = provider_impl.verify(token)

            uid = user_info["uid"]

            existing = SocialAccount.objects.filter(
                provider=provider,
                provider_uid=uid
            ).first()

            if existing and existing.user != request.user:
                return error_response(
                    message="Akun sudah terhubung dengan user lain",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if SocialAccount.objects.filter(
                user=request.user,
                provider=provider
            ).exists():
                return error_response(
                    message=f"Akun {provider} sudah terhubung",
                    status=status.HTTP_400_BAD_REQUEST  
                )
            
            SocialAccount.objects.create(
                user=request.user,
                provider=provider,
                provider_uid=uid
            )

            return success_response(
                message=f"Berhasil Menghubungkan akun {provider}",
                data ={
                    "provider":provider
                },
                status=status.HTTP_201_CREATED
            )
        
        except ValueError as e:
            return error_response(
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        





