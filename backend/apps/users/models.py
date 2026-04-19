from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    location_prefecture = models.CharField(max_length=100, null=True, blank=True)
    location_quartier = models.CharField(max_length=100, null=True, blank=True)
    kyc_level = models.IntegerField(default=1)  # KYC compliance level (1, 2, 3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username