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

    # 🔥 VALIDASI DULU
    if not email:
        raise ValueError("Email tidak tersedia")

    if not user_info.get("email_verified"):
        raise ValueError("Email belum diverifikasi")

    # 🔥 1. PRIORITAS: cek SocialAccount (identity utama)
    social = SocialAccount.objects.filter(
        provider=provider,
        provider_uid=uid
    ).first()

    if social:
        return social.user, False

    # 🔥 2. fallback ke email (untuk linking otomatis)
    user = User.objects.filter(email=email).first()

    if not user:
        user = User.objects.create(
            email=email,
            first_name=user_info.get("first_name", ""),
            last_name=user_info.get("last_name", ""),
            role="buyer",
        )
        user.set_unusable_password()
        user.save()
        created = True
    else:
        created = False

    # 🔥 3. AUTO LINK (INI YANG SEBELUMNYA KAMU LEWATKAN)
    SocialAccount.objects.get_or_create(
        user=user,
        provider=provider,
        provider_uid=uid
    )

    return user, created