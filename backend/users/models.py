from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'ADMIN'
    PROVIDER = 'PROVIDER'
    CUSTOMER = 'CUSTOMER'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (PROVIDER, 'Provider'),
        (CUSTOMER, 'Customer'),
    ]
    
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    avatar = models.URLField(max_length=500, null=True, blank=True, verbose_name="Ảnh đại diện")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.user} - {self.action}"
    
    class Meta:
        ordering = ['-created_at']