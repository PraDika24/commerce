from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
import requests as http_request

class BaseProvider:
    def verify(self, token: str) -> dict:
        raise NotImplementedError


class GoogleProvider(BaseProvider):
    def verify(self, token: str) -> dict:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        return {
            "email": idinfo.get("email"),
            "email_verified": idinfo.get("email_verified", False),
            "first_name": idinfo.get("given_name", ""),
            "last_name": idinfo.get("family_name", ""),
            "uid": idinfo.get("sub"),
        }   

class FacebookProvider(BaseProvider):
    def verify(self, token: str) -> dict:
        url = "https://graph.facebook.com/me"
        params = {
            "fields": "id,email,first_name,last_name",
            "access_token": token
        }

        response = http_request.get(url, params=params, timeout=5)

        if response.status_code != 200:
            raise ValueError("Gagal menghubungi Facebook")

        data = response.json()

        if "error" in data:
            raise ValueError("Token Facebook tidak valid")

        if not data.get("email"):
            raise ValueError("Email tidak tersedia dari Facebook")

        return {
            "email": data["email"],
            "email_verified": True,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "uid": data["id"],
        }


PROVIDERS = {
    "google": GoogleProvider(),
    "facebook": FacebookProvider(),
}