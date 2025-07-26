import pytest
from rest_framework import status
from rest_framework.test import APIClient
from backend.apps.users.models import User
@pytest.fixture(autouse=True)
def disable_throttling_and_csrf(settings):
    """
    Disable DRF throttling and CSRF middleware during tests.
    """
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}
    settings.MIDDLEWARE = [
        mw for mw in settings.MIDDLEWARE if mw != 'django.middleware.csrf.CsrfViewMiddleware'
    ]


@pytest.mark.django_db
class TestUserAuthAPI:
    def setup_method(self):
        self.client = APIClient()

        self.user_password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="testuser@example.com",
            full_name="Test User",
            password=self.user_password
        )

        self.signup_url = "/api/auth/signup/"
        self.login_url = "/api/auth/login/"
        self.csrf_url = "/api/auth/csrf/"

    def test_user_signup_weak_password(self):
        data = {
            "email": "weak@example.com",
            "full_name": "Weak Password User",
            "password": "123",  # Intentionally weak password
        }
        response = self.client.post(self.signup_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_user_login_success(self):
        data = {
            "email": self.user.email,
            "password": self.user_password,
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
