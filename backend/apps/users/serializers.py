from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone_number', 'email', 'profile_picture',
            'location_prefecture', 'location_quartier', 'date_of_birth',
            'kyc_level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'kyc_level', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'phone_number', 'password', 'password_confirm',
            'date_of_birth', 'email'
        ]
    
    def validate_phone_number(self, value):
        """Validate Guinea phone number format (+224XXXXXXXX)"""
        if not value:
            raise serializers.ValidationError('Phone number is required')
        
        # Remove any spaces or dashes
        cleaned = re.sub(r'[\s\-]', '', value)
        
        # Check format
        if not cleaned.startswith('+224'):
            raise serializers.ValidationError('Phone number must start with +224 (Guinea)')
        
        if len(cleaned) != 13:
            raise serializers.ValidationError('Phone number must be 13 digits (+224XXXXXXXX)')
        
        if not cleaned[4:].isdigit():
            raise serializers.ValidationError('Phone number must contain only digits after +224')
        
        return cleaned
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('Password must contain at least one number')
        
        return value
    
    def validate(self, data):
        """Check if passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        
        # Check age (must be at least 18)
        if data.get('date_of_birth'):
            from datetime import date
            today = date.today()
            age = today.year - data['date_of_birth'].year - (
                (today.month, today.day) < (data['date_of_birth'].month, data['date_of_birth'].day)
            )
            if age < 18:
                raise serializers.ValidationError({'date_of_birth': 'You must be at least 18 years old'})
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            date_of_birth=validated_data.get('date_of_birth'),
            email=validated_data.get('email'),
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user data"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = UserSerializer(self.user).data
        
        return data
