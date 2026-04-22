from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    location_prefecture = models.CharField(max_length=100, null=True, blank=True)
    location_quartier = models.CharField(max_length=100, null=True, blank=True)
    kyc_level = models.IntegerField(default=1)  # KYC compliance level (1, 2, 3)
    kyc_invoice_verified = models.BooleanField(default=False)

    # EDG KYC fields
    edg_meter_number = models.CharField(max_length=20, null=True, blank=True)
    edg_nom = models.CharField(max_length=200, null=True, blank=True)
    edg_quartier = models.CharField(max_length=100, null=True, blank=True)
    edg_tranche = models.CharField(max_length=50, null=True, blank=True)
    edg_tarification = models.CharField(max_length=100, null=True, blank=True)
    edg_conso_actuelle = models.FloatField(null=True, blank=True)
    edg_conso_precedente = models.FloatField(null=True, blank=True)
    edg_montant = models.FloatField(null=True, blank=True)
    edg_periode = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username