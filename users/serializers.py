from rest_framework import serializers
import re
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()

class LinkSocialSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()