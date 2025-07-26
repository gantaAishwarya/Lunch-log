from unittest.mock import patch
from datetime import date
import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model

from backend.apps.receipts.models import Receipt
from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from backend.apps.restaurants.tasks import (
    fetch_and_create_restaurant_from_receipt,
    update_user_interaction,
)

User = get_user_model()


@pytest.mark.django_db
class TestRestaurantTasks:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(
            email="testtaskuser@example.com",
            password="testpass",
            full_name="Task User"
        )
        self.receipt = Receipt.objects.create(
            user=self.user,
            restaurant_name="Test Resto",
            address="12345 Berlin Street, Berlin",
            date=date.today(),
            price=Decimal("20.0"),
            image=None,
        )

    @patch("backend.apps.restaurants.tasks.fetch_restaurant_details_from_google")
    def test_fetch_and_create_restaurant_skips_missing_data(self, mock_fetch_google):
        """
        Should skip creating a Restaurant if receipt's city extraction returns None or missing.
        """
        bad_receipt = Receipt.objects.create(
            user=self.user,
            restaurant_name="NoCityResto",
            address="",  # No city info
            date=date.today(),
            price=Decimal("15.0"),
            image=None,
        )
        fetch_and_create_restaurant_from_receipt(bad_receipt.id)
        assert not Restaurant.objects.filter(name="NoCityResto").exists(), \
            "Restaurant should not be created when city info is missing"

    @patch("backend.apps.restaurants.tasks.fetch_restaurant_details_from_google")
    def test_fetch_and_create_restaurant_creates_new(self, mock_fetch_google):
        """
        Should create a new Restaurant and UserRestaurantInteraction when details fetched successfully.
        """
        mock_fetch_google.return_value = {
            "place_id": "abc123",
            "name": "Test Resto",
            "address": "12345 Berlin Street, Berlin",
            "city": "Berlin",
            "cuisine": ["italian"],
            "rating": 4.5,
            "user_ratings_total": 50,
            "phone_number": "+49123456789"
        }

        fetch_and_create_restaurant_from_receipt(self.receipt.id)
        restaurant = Restaurant.objects.filter(place_id="abc123").first()
        assert restaurant is not None, "Restaurant should be created with place_id 'abc123'"
        assert restaurant.name == "Test Resto"
        assert restaurant.city == "Berlin"
        assert restaurant.cuisine == ["italian"]

        interaction = UserRestaurantInteraction.objects.filter(user=self.user, restaurant=restaurant).first()
        assert interaction is not None, "UserRestaurantInteraction should be created"
        assert interaction.visits == 1
        assert interaction.average_spend == Decimal("20.0")

    def test_update_user_interaction_creates_and_updates(self):
        """
        update_user_interaction should create a new interaction or update existing one correctly.
        """
        restaurant = Restaurant.objects.create(
            name="UpdateTest Resto",
            city="Berlin",
        )

        # Create new interaction
        update_user_interaction(self.user, restaurant, date.today(), Decimal("25.0"))
        interaction = UserRestaurantInteraction.objects.get(user=self.user, restaurant=restaurant)
        assert interaction.visits == 1, "Visits count should be 1 after first update"
        assert interaction.average_spend == Decimal("25.0"), "Average spend should equal initial price"

        # Update existing interaction with new visit and price
        update_user_interaction(self.user, restaurant, date.today(), Decimal("35.0"))
        interaction.refresh_from_db()
        assert interaction.visits == 2, "Visits count should be incremented to 2"
        expected_avg = Decimal("30.0")
        assert abs(interaction.average_spend - expected_avg) < Decimal("0.001"), \
            f"Average spend should be updated to {expected_avg}"
