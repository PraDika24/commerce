from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import SellerApplication
from .serializers import SellerApplicationSerializer
from .tasks import send_application_approved_email, send_application_rejected_email
from utils.response import success_response, error_response
from drf_spectacular.utils import extend_schema

class SellerApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    # Buyer ajukan permohonan
    @extend_schema(request=SellerApplicationSerializer)
    def post(self, request):
        serializer = SellerApplicationSerializer(
            data=request.data,
            context={"request": request}
        )
        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user)
        return success_response(
            message="Permohonan berhasil diajukan, tunggu konfirmasi dari admin.",
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )

    # Buyer cek status permohonan
    def get(self, request):
        # Ambil semua permohonan, bukan hanya yang aktif
        applications = SellerApplication.objects.filter(
            user=request.user
        ).order_by("-created_at")

        if not applications.exists():
            return error_response(
                message="Kamu belum mengajukan permohonan",
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerApplicationSerializer(applications, many=True)
        return success_response(
            data=serializer.data,
            message="Riwayat permohonan",
            status=status.HTTP_200_OK,
        )

    # Buyer batalkan permohonan (hanya jika masih pending)
    def delete(self, request):
        application = SellerApplication.objects.filter(
            user=request.user
        ).first()

        if not application:
            return error_response(
                message="Kamu belum mengajukan permohonan",
                status=status.HTTP_404_NOT_FOUND,
            )

        if not application.is_pending:
            return error_response(
                message="Permohonan tidak bisa dibatalkan karena sudah diproses",
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.delete()
        return success_response(
            message="Permohonan berhasil dibatalkan.",
            status=status.HTTP_200_OK,
        )