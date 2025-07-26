from unittest.mock import patch, MagicMock
from datetime import date
import pytest
from backend.apps.receipts.models import Receipt
from backend.apps.restaurants.models import Restaurant, UserRestaurantInteraction
from backend.apps.restaurants.tasks import (
    fetch_and_create_restaurant_from_receipt,
    update_user_interaction,
)
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid


User = get_user_model()

@pytest.mark.django_db
class TestRestaurantTasks:

    def setup_method(self):
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
            price=20.0,
            image=None  # image not needed here
        )

    @patch("backend.apps.restaurants.tasks.fetch_restaurant_details_from_google")
    def test_fetch_and_create_restaurant_skips_missing_data(self, mock_fetch_google):
        # Missing city extraction returns None -> skip
        bad_receipt = Receipt.objects.create(
            user=self.user,
            restaurant_name="NoCityResto",
            address="",
            date=date.today(),
            price=15.0,
            image=None
        )
        fetch_and_create_restaurant_from_receipt(bad_receipt.id)
        assert not Restaurant.objects.filter(name="NoCityResto").exists()

    @patch("backend.apps.restaurants.tasks.fetch_restaurant_details_from_google")
    def test_fetch_and_create_restaurant_creates_new(self, mock_fetch_google):
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
        assert restaurant is not None
        assert restaurant.name == "Test Resto"
        assert restaurant.city == "Berlin"
        assert restaurant.cuisine == ["italian"]

        interaction = UserRestaurantInteraction.objects.filter(user=self.user, restaurant=restaurant).first()
        assert interaction is not None
        assert interaction.visits == 1
        assert interaction.average_spend == 20.0

    def test_update_user_interaction_creates_and_updates(self):
        restaurant = Restaurant.objects.create(
            name="UpdateTest Resto",
            city="Berlin",
        )

        # Create new interaction
        update_user_interaction(self.user, restaurant, date.today(), Decimal("25.0"))
        interaction = UserRestaurantInteraction.objects.get(user=self.user, restaurant=restaurant)
        assert interaction.visits == 1
        assert interaction.average_spend == Decimal("25.0")

        # Update existing interaction with new visit and price 35.0 for average calculation
        update_user_interaction(self.user, restaurant, date.today(), Decimal("35.0"))
        interaction.refresh_from_db()
        assert interaction.visits == 2
        # Average spend updated correctly: (25 + 35) / 2 = 30
        assert abs(interaction.average_spend - Decimal("30.0")) < Decimal("0.001")
