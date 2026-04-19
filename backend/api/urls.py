from django.urls import path
from . import views

urlpatterns = [
    path('upload-invoice/', views.upload_invoice, name='upload-invoice'),
    path('capture-meter/', views.capture_meter, name='capture-meter'),
    path('validate-reading/', views.validate_reading, name='validate-reading'),
]