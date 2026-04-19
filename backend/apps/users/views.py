from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Registration successful. Please login.',
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)


class LoginView(CustomTokenObtainPairSerializer):
    """
    API endpoint for user login (JWT tokens).
    POST /api/login/
    
    Returns:
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": { ... user data ... }
    }
    """
    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile.
    GET/PUT /api/profile/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    """
    API endpoint for user logout.
    POST /api/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Client should delete tokens on their side
        # For blacklist implementation, add django-rest-framework-simplejwt blacklist
        return Response({
            'success': True,
            'message': 'Logout successful',
        }, status=status.HTTP_200_OK)
