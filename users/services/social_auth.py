from django.contrib.auth import get_user_model
from users.models import SocialAccount
from .provider import PROVIDERS

User = get_user_model()


def social_authenticate(provider: str, token: str):
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

    # 🔥 1. cek SocialAccount → LOGIN
    social = SocialAccount.objects.filter(
        provider=provider,
        provider_uid=uid
    ).select_related("user").first()

    if social:
        return social.user, False

    # 🔥 2. cek email → JANGAN create user baru
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        raise ValueError(
            "Email sudah terdaftar. Silakan login lalu hubungkan akun."
        )

    # 🔥 3. REGISTER (hanya sekali, email pertama yang disimpan)
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

    return user, True

