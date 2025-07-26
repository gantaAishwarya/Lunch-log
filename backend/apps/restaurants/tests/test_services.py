from datetime import date
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from backend.apps.restaurants.services import (
    fetch_restaurant_details_from_google,
    get_recommendations_for_user,
)

User = get_user_model()


class MockResponse:
    def __init__(self, json_data: dict, status_code: int):
        self._json = json_data
        self.status_code = status_code

    def json(self) -> dict:
        return self._json


class TestRestaurantServices(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="serviceuser@example.com",
            password="testpass123",
            full_name="Service User"
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="pass",
            full_name="Other User"
        )
        cls.city = "Berlin"

        cls.restaurant1 = Restaurant.objects.create(
            name="Pasta Palace",
            address="123 Main St, Berlin",
            city=cls.city,
            rating=4.5,
        )
        cls.restaurant2 = Restaurant.objects.create(
            name="Sushi Haus",
            address="456 Sushi St, Berlin",
            city=cls.city,
            rating=4.2,
        )
        cls.restaurant3 = Restaurant.objects.create(
            name="Taco Town",
            address="789 Taco Blvd, Berlin",
            city=cls.city,
            rating=4.0,
        )

    def test_get_recommendations_with_user_interactions(self):
        """
        Recommendations should include restaurants user has interacted with,
        as well as other relevant restaurants.
        """
        UserRestaurantInteraction.objects.create(
            user=self.user,
            restaurant=self.restaurant1,
            visits=5,
            last_visited=date.today()
        )
        UserRestaurantInteraction.objects.create(
            user=self.user,
            restaurant=self.restaurant2,
            visits=3,
            last_visited=date.today()
        )
        UserRestaurantInteraction.objects.create(
            user=self.other_user,
            restaurant=self.restaurant3,
            visits=10,
            last_visited=date.today()
        )

        recommendations = get_recommendations_for_user(self.user, city=self.city)
        recommendation_names = [r.name for r in recommendations]

        self.assertIn("Pasta Palace", recommendation_names)
        self.assertIn("Sushi Haus", recommendation_names)
        self.assertIn("Taco Town", recommendation_names)

    def test_get_recommendations_with_no_data_fallback(self):
        """
        When user has no interactions, fallback to returning restaurants
        available in the specified city.
        """
        UserRestaurantInteraction.objects.all().delete()

        recommendations = get_recommendations_for_user(self.user, city=self.city)

        self.assertGreater(len(recommendations), 0)
        self.assertTrue(all(r.city == self.city for r in recommendations))

    @patch("backend.apps.restaurants.services.requests.get")
    def test_fetch_restaurant_details_from_google(self, mock_get):
        """
        Test that fetching restaurant details from Google Places API
        returns expected parsed data.
        """
        mock_get.side_effect = [
            MockResponse({
                "candidates": [{"place_id": "abc123"}]
            }, 200),
            MockResponse({
                "result": {
                    "place_id": "abc123",
                    "name": "Test Resto",
                    "formatted_address": "123 Main St, Berlin",
                    "formatted_phone_number": "+49123456789",
                    "rating": 4.6,
                    "user_ratings_total": 100,
                    "types": ["restaurant", "food", "italian"]
                }
            }, 200)
        ]

        result = fetch_restaurant_details_from_google("Test Resto", self.city)

        self.assertEqual(result["place_id"], "abc123")
        self.assertEqual(result["name"], "Test Resto")
        self.assertEqual(result["city"], self.city)
        self.assertIn("italian", result["cuisine"])
