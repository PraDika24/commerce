from django.db import models
from django.conf import settings
from django.utils.text import slugify

class SellerApplication(models.Model):

    STATUS_CHOICES = [
        ("pending",  "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user        = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    related_name="seller_applications"
                  )
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reason      = models.TextField(help_text="Alasan ingin menjadi seller")
    reject_note = models.TextField(blank=True, null=True, help_text="Alasan ditolak admin")
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Seller Application"
        verbose_name_plural = "Seller Applications"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    @property
    def is_pending(self):
        return self.status == "pending"

    @property
    def is_approved(self):
        return self.status == "approved"

    @property
    def is_rejected(self):
        return self.status == "rejected"

class Store(models.Model):

    seller      = models.OneToOneField(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    related_name="store",
                    limit_choices_to={"role": "seller"}
                  )
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    logo        = models.ImageField(
                    upload_to="stores/logos/",
                    blank=True,
                    null=True
                  )
    address     = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Store"
        verbose_name_plural = "Stores"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto generate slug dari nama toko
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)