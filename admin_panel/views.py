from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status

from sellers.models import SellerApplication
from sellers.tasks import (
    send_application_approved_email,
    send_application_rejected_email,
)
from .permissions import IsAdmin
from .serializers import SellerApplicationDetailSerializer, ReviewApplicationSerializer
from utils.response import success_response, error_response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminSellerApplicationListView(APIView):
    permission_classes = [IsAdmin]

    # Lihat semua permohonan (bisa filter by status)
    def get(self, request):
        status_filter = request.query_params.get("status", "pending")

        VALID_STATUS = ["pending", "approved", "rejected"]
        if status_filter not in VALID_STATUS:
            return error_response(
                message=f"Status tidak valid. Pilih: {', '.join(VALID_STATUS)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        applications = SellerApplication.objects.filter(
            status=status_filter
        ).select_related("user").order_by("created_at")

        serializer = SellerApplicationDetailSerializer(applications, many=True)
        return success_response(
            data=serializer.data,
            message=f"{applications.count()} permohonan {status_filter}",
            status=status.HTTP_200_OK,
        )


class AdminSellerApplicationDetailView(APIView):
    permission_classes = [IsAdmin]

    # Lihat detail satu permohonan
    def get(self, request, pk):
        application = SellerApplication.objects.filter(
            pk=pk
        ).select_related("user").first()

        if not application:
            return error_response(
                message="Permohonan tidak ditemukan",
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SellerApplicationDetailSerializer(application)
        return success_response(
            data=serializer.data,
            message="Detail permohonan",
            status=status.HTTP_200_OK,
        )

    # Approve / Reject permohonan
    @extend_schema(request=ReviewApplicationSerializer)
    def patch(self, request, pk):
        application = SellerApplication.objects.filter(
            pk=pk
        ).select_related("user").first()

        if not application:
            return error_response(
                message="Permohonan tidak ditemukan",
                status=status.HTTP_404_NOT_FOUND,
            )

        if not application.is_pending:
            return error_response(
                message="Permohonan sudah diproses sebelumnya",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation Error",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision    = serializer.validated_data["status"]
        reject_note = serializer.validated_data.get("reject_note", "")

        if decision == "approved":
            application.status = "approved"
            application.save(update_fields=["status", "updated_at"])

            # Update role user jadi seller
            application.user.role = "seller"
            application.user.save(update_fields=["role"])

            send_application_approved_email.delay(application.user.email)

            return success_response(
                message=f"Permohonan {application.user.email} berhasil disetujui.",
                status=status.HTTP_200_OK,
            )

        elif decision == "rejected":
            application.status      = "rejected"
            application.reject_note = reject_note
            application.is_active   = False        # ← nonaktifkan, tidak dihapus
            application.save(update_fields=["status", "reject_note", "is_active", "updated_at"])

            send_application_rejected_email.delay(application.user.email, reject_note)

            return success_response(
                message=f"Permohonan {application.user.email} berhasil ditolak.",
                status=status.HTTP_200_OK,
            )