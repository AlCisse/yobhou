from django.urls import path
from apps.payments import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('confirm/', views.confirm_payment, name='confirm_payment'),
    path('status/<ref>/', views.payment_status, name='payment_status'),
    path('receipts/', views.list_receipts, name='list_receipts'),
    path('receipts/<int:payment_id>/pdf/', views.download_receipt, name='download_receipt'),
]
