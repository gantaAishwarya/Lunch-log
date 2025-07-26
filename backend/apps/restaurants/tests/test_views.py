import pytest
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from datetime import date

User = get_user_model()


class FoodRecommendationViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="securepass123",
            full_name="Test User"
        )
        cls.r1 = Restaurant.objects.create(name="Sushi Haus", city="Berlin", cuisine="Japanese")
        cls.r2 = Restaurant.objects.create(name="Pasta Palace", city="Dortmund", cuisine="Italian")
        cls.r3 = Restaurant.objects.create(name="Biryani Spot", city="Hamburg", cuisine="Indian")
        UserRestaurantInteraction.objects.create(
            user=cls.user,
            restaurant=cls.r1,
            last_visited=date.today()
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("food-recommendations")

    def test_recommendation_success(self) -> None:
        """
        Should return 200 and list of recommended restaurants for given city,
        including restaurants visited by user and excluding others.
        """
        response = self.client.get(self.url, {"city": "Berlin"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

        restaurant_names = [r["name"] for r in response.data]

        self.assertIn("Sushi Haus", restaurant_names, "Visited restaurant should appear in recommendations")
        self.assertNotIn("Pasta Palace", restaurant_names, "Restaurants outside city should not appear")
        self.assertNotIn("Biryani Spot", restaurant_names, "Restaurants outside city should not appear")

    def test_missing_city_param(self) -> None:
        """
        Should return 400 BAD REQUEST if city param is missing.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "City is required")

    def test_requires_authentication(self) -> None:
        """
        Should return 403 FORBIDDEN if request is unauthenticated.
        """
        self.client.logout()
        response = self.client.get(self.url, {"city": "Berlin"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
