from rest_framework import serializers
import re
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()

class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()

class LinkSocialSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah digunakan")
        return value

    def validate_first_name(self, value):
        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "First name hanya boleh huruf dan spasi"
            )
        return value

    def validate_last_name(self, value):
        if not re.match(r'^[A-Za-z ]+$', value):
            raise serializers.ValidationError(
                "Last name hanya boleh huruf dan spasi"
            )
        return value

    # 🔹 Validasi password
    def validate_password(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password minimal 8 karakter") 

        if not re.search(r'[A-Z]', value):
           errors.append("Harus ada huruf besar")

        if not re.search(r'[0-9]', value):
            errors.append("Harus ada angka")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>_]', value):
            errors.append("Harus ada karakter spesial")

        if errors:
            raise serializers.ValidationError(errors)
        return value

    # 🔹 Create user (hash password)
    def create(self, validated_data):
       
       password = validated_data.get("password")
       if not password:
            raise serializers.ValidationError("Password wajib diisi")
       return  User.objects.create_user(
           **validated_data,
            role="buyer"
        )

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
    