from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from backend.apps.restaurants.services import (
    fetch_restaurant_details_from_google,
    get_recommendations_for_user,
)
from unittest.mock import patch
from rest_framework.test import APITestCase
import pytest
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from datetime import date

User = get_user_model()

class TestRestaurantServices(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="serviceuser@example.com",
            password="testpass123",
            full_name="Service User"
        )

        self.city = "Berlin"

        self.restaurant1 = Restaurant.objects.create(
            name="Pasta Palace",
            address="123 Main St, Berlin",
            city="Berlin",
            rating=4.5,
        )

        self.restaurant2 = Restaurant.objects.create(
            name="Sushi Haus",
            address="456 Sushi St, Berlin",
            city="Berlin",
            rating=4.2,
        )

        self.restaurant3 = Restaurant.objects.create(
            name="Taco Town",
            address="789 Taco Blvd, Berlin",
            city="Berlin",
            rating=4.0,
        )

    def test_get_recommendations_with_user_interactions(self):
        UserRestaurantInteraction.objects.create(
            user=self.user,
            restaurant=self.restaurant1,
            visits=5,
            last_visited=date.today()  # <-- Add this to satisfy NOT NULL constraint
        )
        UserRestaurantInteraction.objects.create(
            user=self.user,
            restaurant=self.restaurant2,
            visits=3,
            last_visited=date.today()
        )
        UserRestaurantInteraction.objects.create(
            user=User.objects.create_user(
                email="other@example.com",
                password="pass",
                full_name="Other User"
            ),
            restaurant=self.restaurant3,
            visits=10,
            last_visited=date.today()
        )

        recommendations = get_recommendations_for_user(self.user, city="Berlin")
        recommendation_names = [r.name for r in recommendations]

        assert "Pasta Palace" in recommendation_names
        assert "Sushi Haus" in recommendation_names
        assert "Taco Town" in recommendation_names

    def test_get_recommendations_with_no_data_fallback(self):
        # Clear all interactions
        UserRestaurantInteraction.objects.all().delete()
        recommendations = get_recommendations_for_user(self.user, city="Berlin")
        assert len(recommendations) > 0
        assert all(r.city == "Berlin" for r in recommendations)

    @patch("backend.apps.restaurants.services.requests.get")
    def test_fetch_restaurant_details_from_google(self, mock_get):
        mock_get.side_effect = [
            # First call - text search
            MockResponse({
                "candidates": [{"place_id": "abc123"}]
            }, 200),
            # Second call - place details
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

        result = fetch_restaurant_details_from_google("Test Resto", "Berlin")

        assert result["place_id"] == "abc123"
        assert result["name"] == "Test Resto"
        assert result["city"] == "Berlin"
        assert "italian" in result["cuisine"]


class MockResponse:
    def __init__(self, json_data, status_code):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json