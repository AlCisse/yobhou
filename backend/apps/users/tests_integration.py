"""
Yobhou Fintech - API Integration Tests
Tests for authentication and user management endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


@pytest.mark.django_db
class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client instance"""
        return APIClient()
    
    @pytest.fixture
    def user_credentials(self):
        """Valid user credentials for testing"""
        return {
            'username': 'testuser',
            'phone_number': '+224601234567',
            'password': 'Test1234',
            'password_confirm': 'Test1234',
            'date_of_birth': '1990-01-01',
        }
    
    def test_health_check_endpoint(self, api_client):
        """Test health check endpoint (no auth required)"""
        url = reverse('health-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'
        assert 'timestamp' in response.data
        assert response.data['version'] == '1.0.0'
    
    def test_user_registration_success(self, api_client, user_credentials):
        """Test successful user registration"""
        url = reverse('register')
        response = api_client.post(url, user_credentials, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'user_id' in response.data
        
        # Verify user was created in database
        assert User.objects.filter(username='testuser').exists()
    
    def test_user_registration_duplicate_phone(self, api_client, user_credentials):
        """Test registration with duplicate phone number"""
        url = reverse('register')
        
        # First registration
        api_client.post(url, user_credentials, format='json')
        
        # Second registration with same phone
        duplicate_credentials = user_credentials.copy()
        duplicate_credentials['username'] = 'testuser2'
        response = api_client.post(url, duplicate_credentials, format='json')
        
        # Should fail (phone number must be unique)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_weak_password(self, api_client):
        """Test registration with weak password"""
        url = reverse('register')
        
        weak_credentials = {
            'username': 'testuser',
            'phone_number': '+224601234567',
            'password': 'weak',  # Too short
            'password_confirm': 'weak',
            'date_of_birth': '1990-01-01',
        }
        
        response = api_client.post(url, weak_credentials, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_user_registration_invalid_phone(self, api_client):
        """Test registration with invalid phone number"""
        url = reverse('register')
        
        invalid_phone = {
            'username': 'testuser',
            'phone_number': '+33612345678',  # Not Guinea (+224)
            'password': 'Test1234',
            'password_confirm': 'Test1234',
            'date_of_birth': '1990-01-01',
        }
        
        response = api_client.post(url, invalid_phone, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone_number' in response.data
    
    def test_user_registration_underage(self, api_client):
        """Test registration with underage user"""
        url = reverse('register')
        
        underage = {
            'username': 'younguser',
            'phone_number': '+224601234567',
            'password': 'Test1234',
            'password_confirm': 'Test1234',
            'date_of_birth': str(date.today().year - 16),  # 16 years old
        }
        
        response = api_client.post(url, underage, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'date_of_birth' in response.data
    
    def test_login_success(self, api_client, user_credentials):
        """Test successful login"""
        # Register user first
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        # Login
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'Test1234'
        }
        response = api_client.post(login_url, login_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, api_client, user_credentials):
        """Test login with invalid credentials"""
        # Register user first
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        # Login with wrong password
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword123'
        }
        response = api_client.post(login_url, login_data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_refresh(self, api_client, user_credentials):
        """Test token refresh"""
        # Register and login
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        login_url = reverse('login')
        login_response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'Test1234'
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        
        # Refresh token
        refresh_url = reverse('token_refresh')
        response = api_client.post(refresh_url, {
            'refresh': refresh_token
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_get_user_profile(self, api_client, user_credentials):
        """Test getting user profile (authenticated)"""
        # Register and login
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        login_url = reverse('login')
        login_response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'Test1234'
        }, format='json')
        
        access_token = login_response.data['access']
        
        # Get profile
        profile_url = reverse('profile')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.get(profile_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['phone_number'] == '+224601234567'
    
    def test_update_user_profile(self, api_client, user_credentials):
        """Test updating user profile"""
        # Register and login
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        login_url = reverse('login')
        login_response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'Test1234'
        }, format='json')
        
        access_token = login_response.data['access']
        
        # Update profile
        profile_url = reverse('profile')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(profile_url, {
            'username': 'testuser',
            'phone_number': '+224601234567',
            'email': 'testuser@example.com',
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'testuser@example.com'
    
    def test_logout(self, api_client, user_credentials):
        """Test user logout"""
        # Register and login
        register_url = reverse('register')
        api_client.post(register_url, user_credentials, format='json')
        
        login_url = reverse('login')
        login_response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'Test1234'
        }, format='json')
        
        access_token = login_response.data['access']
        
        # Logout
        logout_url = reverse('logout')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(logout_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
    
    def test_unauthorized_access(self, api_client):
        """Test accessing protected endpoint without auth"""
        profile_url = reverse('profile')
        response = api_client.get(profile_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestOCREndpoints:
    """Integration tests for OCR endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Create API client with authenticated user"""
        client = APIClient()
        
        # Create user and login
        user = User.objects.create_user(
            username='ocrtestuser',
            phone_number='+224601234568',
            password='Test1234'
        )
        
        login_response = client.post(reverse('login'), {
            'username': 'ocrtestuser',
            'password': 'Test1234'
        }, format='json')
        
        access_token = login_response.data['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        return client
    
    def test_upload_invoice_missing_file(self, api_client):
        """Test invoice upload without file"""
        url = reverse('upload-invoice')
        response = api_client.post(url, {}, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'invoice file' in str(response.data)
    
    def test_capture_meter_missing_file(self, api_client):
        """Test meter capture without file"""
        url = reverse('capture-meter')
        response = api_client.post(url, {}, format='multipart')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'meter photo' in str(response.data)
    
    def test_validate_reading_missing_fields(self, api_client):
        """Test reading validation with missing fields"""
        url = reverse('validate-reading')
        response = api_client.post(url, {
            'meter_number': '12345678'
            # Missing current_index
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'current_index' in str(response.data)
    
    def test_validate_reading_invalid_indices(self, api_client):
        """Test reading validation with invalid indices"""
        url = reverse('validate-reading')
        response = api_client.post(url, {
            'meter_number': '12345678',
            'current_index': '100',
            'previous_index': '200',  # Greater than current
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'greater than' in str(response.data)
