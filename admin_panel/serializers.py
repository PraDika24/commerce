from rest_framework import serializers
from sellers.models import SellerApplication
from django.contrib.auth import get_user_model

User = get_user_model()


class SellerApplicationDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk admin melihat detail permohonan."""

    user_email      = serializers.EmailField(source="user.email",       read_only=True)
    user_first_name = serializers.CharField(source="user.first_name",   read_only=True)
    user_last_name  = serializers.CharField(source="user.last_name",    read_only=True)
    user_joined     = serializers.DateTimeField(source="user.date_joined", read_only=True)

    class Meta:
        model  = SellerApplication
        fields = [
            "id",
            "user_email",
            "user_first_name",
            "user_last_name",
            "user_joined",
            "reason",
            "status",
            "reject_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewApplicationSerializer(serializers.Serializer):
    """Serializer untuk admin approve/reject permohonan."""

    STATUS_CHOICES = ["approved", "rejected"]

    status      = serializers.ChoiceField(choices=STATUS_CHOICES)
    reject_note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == "rejected" and not attrs.get("reject_note", "").strip():
            raise serializers.ValidationError(
                {"reject_note": "Alasan penolakan wajib diisi"}
            )
        return attrs