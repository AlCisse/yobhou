from django.db import models
from apps.users.models import User


class MeterReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meter_number = models.CharField(max_length=20)
    previous_index = models.FloatField()
    current_index = models.FloatField()
    consumption = models.FloatField()
    meter_photo = models.ImageField(upload_to='meter_photos/')
    ocr_data = models.JSONField()  # Store raw OCR data
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reading for meter {self.meter_number} by {self.user.username}"