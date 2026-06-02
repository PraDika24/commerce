from rest_framework import serializers
import re
from django.contrib.auth import get_user_model
from .models import User
from .tasks import send_verification_email

User = get_user_model()

class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()

class LinkSocialSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()


SPECIAL_CHARS = r'[!@#$%^&*()\-,.?\":{}|<>_~]'
NAME_REGEX    = r'^[A-Za-z ]+$'
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "first_name": {"required": True, "max_length": 100},
            "last_name":  {"required": True, "max_length": 100},
        }

    @staticmethod
    def _validate_name(value: str, field_label: str) -> str:
        """Strip whitespace, enforce alpha-only, block empty strings."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError(f"{field_label} tidak boleh kosong")
        if not re.match(NAME_REGEX, value):
            raise serializers.ValidationError(
                f"{field_label} hanya boleh berisi huruf dan spasi"
            )
        return value
    

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah digunakan")
        return value

    def validate_first_name(self, value: str) -> str:
        return self._validate_name(value, "First name")

    def validate_last_name(self, value: str) -> str:
        return self._validate_name(value, "Last name")


    # 🔹 Validasi password
    def validate_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password minimal 8 karakter") 
        if not re.search(r'[a-z]', value):        # ← tambahan: huruf kecil
            errors.append("Harus ada huruf kecil")
        if not re.search(r'[A-Z]', value):
           errors.append("Harus ada huruf besar")

        if not re.search(r'[0-9]', value):
            errors.append("Harus ada angka")

        if not re.search(SPECIAL_CHARS, value):
            errors.append("Harus ada karakter spesial")

        if errors:
            raise serializers.ValidationError(errors)
        return value

    # 🔹 Create user (hash password)
    def create(self, validated_data):
       
       password = validated_data.get("password")
       if not password:
            raise serializers.ValidationError("Password wajib diisi")
       user =  User.objects.create_user(
           **validated_data,
            is_active=False,
            role="buyer"
        )
       send_verification_email.delay(user.email)
       return user
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError(
                "Email atau Password Salah"
            )
        
        if not user.has_usable_password():
            raise serializers.ValidationError(
                "Akun ini terdaftar menggunakan Google/Facebook. Silakan login menggunakan social login."
            )
        
        if not user.check_password(password):
            raise serializers.ValidationError(
                "Email atau Password Salah"
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User Tidak Aktif"
            )
        
        data['user']= user
        return data
    
class LogOutSerializer(serializers.Serializer):
    token = serializers.CharField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields= ["first_name", "last_name", "address", "phone_number", "profile_image"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "address": {"required": False},
            "phone_number": {"required": False},
            "profile_image": {"required": False},
        }
    
    def validate(self, attrs):
        if 'email' in attrs:
            raise serializers.ValidationError("Email tidak boleh di ubah")
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()

class ResetPasswordSerializer(serializers.Serializer):
    token    = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password minimal 8 karakter")
        if not re.search(r'[A-Z]', value):
            errors.append("Harus ada huruf besar")
        if not re.search(r'[a-z]', value):
            errors.append("Harus ada huruf kecil")
        if not re.search(r'[0-9]', value):
            errors.append("Harus ada angka")
        if not re.search(SPECIAL_CHARS, value):
            errors.append("Harus ada karakter spesial")
        if errors:
            raise serializers.ValidationError(errors)
        return value

# serializers.py
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password minimal 8 karakter")
        if not re.search(r'[A-Z]', value):
            errors.append("Harus ada huruf besar")
        if not re.search(r'[a-z]', value):
            errors.append("Harus ada huruf kecil")
        if not re.search(r'[0-9]', value):
            errors.append("Harus ada angka")
        if not re.search(SPECIAL_CHARS, value):
            errors.append("Harus ada karakter spesial")
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "Password baru tidak boleh sama dengan password lama"}
            )
        return attrs
    

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()
        user  = User.objects.filter(email=value).first()

        if not user:
            raise serializers.ValidationError("Email tidak terdaftar")

        if user.is_active and user.email_verified:
            raise serializers.ValidationError("Email sudah diverifikasi")

        return value

# serializers.py
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        user = self.context["request"].user

        # Kalau punya password — wajib kirim password
        if user.has_usable_password():
            password = attrs.get("password")

            if not password:
                raise serializers.ValidationError(
                    {"password": "Password diperlukan untuk menghapus akun"}
                )

            if not user.check_password(password):
                raise serializers.ValidationError(
                    {"password": "Password tidak sesuai"}
                )

        return attrs