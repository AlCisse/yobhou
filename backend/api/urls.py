from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import RegisterView, UserProfileView, LogoutView
from . import views

# Custom login view (TokenObtainPairView subclass)
from apps.users.views import LoginView as CustomLoginView

urlpatterns = [
    # Health check (no auth required)
    path('health/', views.health_check, name='health-check'),
    
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('complete-registration/', views.complete_registration, name='complete-registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # OCR endpoints
    path('upload-invoice/', views.upload_invoice, name='upload-invoice'),
    path('capture-meter/', views.capture_meter, name='capture-meter'),
    path('validate-reading/', views.validate_reading, name='validate-reading'),
    
    # Payment endpoints
    path('payment/', include('apps.payments.urls')),
]
