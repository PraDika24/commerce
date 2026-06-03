from django.db import models
from django.conf import settings


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
