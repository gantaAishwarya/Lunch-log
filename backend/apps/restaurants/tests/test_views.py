import pytest
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from datetime import date

User = get_user_model()

class FoodRecommendationViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="test@example.com",
            password="securepass123",
            full_name="Test User"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("food-recommendations")

        # Create restaurants
        self.r1 = Restaurant.objects.create(name="Sushi Haus", city="Berlin", cuisine="Japanese")
        self.r2 = Restaurant.objects.create(name="Pasta Palace", city="Dortmund", cuisine="Italian")
        self.r3 = Restaurant.objects.create(name="Biryani Spot", city="Hamburg", cuisine="Indian")

        # Simulate user visited r1
        UserRestaurantInteraction.objects.create(
            user=self.user,
            restaurant=self.r1,
            last_visited=date.today()
        )

    def test_recommendation_success(self):
        response = self.client.get(self.url, {"city": "Berlin"})
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1
        names = [r["name"] for r in response.data]
        assert "Sushi Haus" in names 
        assert "Pasta Palace" not in names
        assert "Biryani Spot" not in names

    def test_missing_city_param(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "City is required"

    def test_requires_authentication(self):
        self.client.logout()
        response = self.client.get(self.url, {"city": "Berlin"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

