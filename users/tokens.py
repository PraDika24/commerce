from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
import secrets
from django.core.cache import cache

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def generate_verification_token(email: str) -> str:
    return serializer.dumps(email, salt="email-verification")

def confirm_verification_token(token: str) -> str | None:
    try:
        email = serializer.loads(
            token,
            salt="email-verification",
            max_age=settings.EMAIL_VERIFICATION_TIMEOUT,
        )
        return email
    except Exception:
        return None

def generate_password_reset_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    cache_key = f"password_reset:{token}"
    cache.set(cache_key, user_id, timeout=settings.PASSWORD_RESET_TIMEOUT)
    return token

def verify_password_reset_token(token: str) -> int | None:
    cache_key = f"password_reset:{token}"
    user_id = cache.get(cache_key)
    return user_id

def delete_password_reset_token(token: str):
    cache.delete(f"password_reset:{token}")