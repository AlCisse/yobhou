import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            phone_number='+224601234567',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.phone_number == '+224601234567'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='admin',
            phone_number='+224601234567',
            password='adminpass123'
        )
        assert admin.is_staff
        assert admin.is_superuser


@pytest.mark.django_db
class TestAuthEndpoints:
    def test_user_registration(self):
        client = APIClient()
        response = client.post('/api/register/', {
            'username': 'newuser',
            'phone_number': '+224601234567',
            'password': 'newpass123',
            'date_of_birth': '1990-01-01'
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_user_login(self):
        client = APIClient()
        User.objects.create_user(
            username='testuser',
            phone_number='+224601234567',
            password='testpass123'
        )
        response = client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
