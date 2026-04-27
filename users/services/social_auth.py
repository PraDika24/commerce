from django.contrib.auth import get_user_model
from users.models import SocialAccount
from .provider import PROVIDERS

User = get_user_model()


def social_login(provider: str, token: str):
    if provider not in PROVIDERS:
        raise ValueError("Provider tidak didukung")

    provider_impl = PROVIDERS[provider]
    user_info = provider_impl.verify(token)

    uid = user_info.get("uid")

    # 🔥 LOGIN HARUS BERDASARKAN UID
    social = SocialAccount.objects.filter(
        provider=provider,
        provider_uid=uid
    ).select_related("user").first()

    if not social:
        raise ValueError("Akun belum terdaftar, silakan register atau link akun")

    return social.user


def social_register(provider: str, token: str):
    if provider not in PROVIDERS:
        raise ValueError("Provider tidak didukung")

    provider_impl = PROVIDERS[provider]
    user_info = provider_impl.verify(token)

    email = user_info.get("email")
    uid = user_info.get("uid")

    if not email:
        raise ValueError("Email tidak tersedia")

    if not user_info.get("email_verified"):
        raise ValueError("Email belum diverifikasi")

    # ❗ jangan duplicate provider
    if SocialAccount.objects.filter(
        provider=provider,
        provider_uid=uid
    ).exists():
        raise ValueError("Akun sudah terdaftar")

    # ❗ jangan duplicate email
    if User.objects.filter(email=email).exists():
        raise ValueError("Email sudah digunakan, silakan login lalu link akun")

    user = User.objects.create(
        email=email,
        first_name=user_info.get("first_name", ""),
        last_name=user_info.get("last_name", ""),
        role="buyer",
    )
    user.set_unusable_password()
    user.save()

    SocialAccount.objects.create(
        user=user,
        provider=provider,
        provider_uid=uid
    )

    return user


