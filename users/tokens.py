from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

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