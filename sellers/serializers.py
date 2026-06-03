from rest_framework import serializers
from .models import SellerApplication


class SellerApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = SellerApplication
        fields = [
            "id",
            "reason",
            "status",
            "reject_note",
            "is_active",      
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "reject_note",
            "is_active",      
            "created_at",
            "updated_at",
        ]

    def validate_reason(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                "Alasan minimal 20 karakter"
            )
        if len(value) > 500:
            raise serializers.ValidationError(
                "Alasan maksimal 500 karakter"
            )
        return value

    def validate(self, attrs):
        user = self.context["request"].user

        # Cek role harus buyer
        if user.role != "buyer":
            raise serializers.ValidationError(
                "Hanya buyer yang bisa mengajukan permohonan"
            )

        # Cek hanya permohonan yang aktif
        existing = SellerApplication.objects.filter(
            user=user,
            is_active=True    # ← hanya cek yang aktif
        ).first()

        if existing:
            if existing.is_pending:
                raise serializers.ValidationError(
                    "Permohonan kamu sedang diproses, harap tunggu"
                )
            if existing.is_approved:
                raise serializers.ValidationError(
                    "Kamu sudah menjadi seller"
                )

        return attrs