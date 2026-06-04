from rest_framework import serializers
from .models import SellerApplication, Store
from django.utils.text import slugify


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

class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Store
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Nama toko minimal 3 karakter"
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                "Nama toko maksimal 100 karakter"
            )

        # Cek nama toko sudah dipakai (exclude toko milik user sendiri saat update)
        qs = Store.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Nama toko sudah digunakan"
            )

        return value

    def validate(self, attrs):
        user = self.context["request"].user

        # Cek role harus seller
        if user.role != "seller":
            raise serializers.ValidationError(
                "Hanya seller yang bisa membuat toko"
            )

        # Cek sudah punya toko (hanya saat create, bukan update)
        if not self.instance:
            if Store.objects.filter(seller=user).exists():
                raise serializers.ValidationError(
                    "Kamu sudah memiliki toko"
                )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["seller"] = user
        validated_data["slug"]   = slugify(validated_data["name"])
        return super().create(validated_data)


class StorePublicSerializer(serializers.ModelSerializer):
    """Serializer untuk publik — tanpa info sensitif."""

    class Meta:
        model  = Store
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "address",
            "created_at",
        ]