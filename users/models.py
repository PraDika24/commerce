from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email wajib diisi")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_USER = (
        ('admin', 'Admin'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller')
    )

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=ROLE_USER, default='buyer')
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    is_mfa_enabled = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    profile_image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    email_verified = models.BooleanField(
        default=False
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

class SocialAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=20, db_index=True)  # google / facebook
    provider_uid = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=['provider', 'provider_uid'], 
            name='unique_social_account'
            ),
        models.UniqueConstraint(
                fields=['user', 'provider'],
                name='unique_user_provider'
            )
    ]
        

    def __str__(self):
        return f"{self.provider} - {self.user}"
    
class EmailVerificationToken(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )