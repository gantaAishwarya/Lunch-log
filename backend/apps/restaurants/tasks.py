import logging
import re
from celery import shared_task
from django.db import transaction
from backend.apps.receipts.models import Receipt
from .models import Restaurant, UserRestaurantInteraction
from .services import fetch_restaurant_details_from_google

logger = logging.getLogger(__name__)

def extract_city_from_address(address):
    if not address:
        return None

    match = re.search(r"\b\d{5}\s+([A-Za-zäöüÄÖÜß\s\-]+)", address)
    if match:
        return match.group(1).strip()

    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 2:
        return parts[-2]

    return None

@shared_task
def fetch_and_create_restaurant_from_receipt(receipt_id):
    try:
        receipt = Receipt.objects.get(id=receipt_id)
        name = receipt.restaurant_name.strip()
        print(f'address is {receipt.address}')
        city = extract_city_from_address(receipt.address)
        logger.info(f"Processing receipt {receipt_id}: restaurant='{name}', city='{city}'")

        if not name or not city:
            logger.warning(f"Skipping receipt {receipt_id} due to missing name or city")
            return

        # Try to find by name and city first
        restaurant = Restaurant.objects.filter(name__iexact=name, city__iexact=city).first()

        if not restaurant:
            # Fetch from Google first to get place_id and other data
            data = fetch_restaurant_details_from_google(name, city)
            if not data or not data.get('place_id'):
                logger.warning(f"Skipping creation: No valid place_id from Google for {name} in {city}")
                return

            # Create restaurant with valid place_id and data from Google
            restaurant = Restaurant.objects.create(
                place_id=data['place_id'],
                name=data.get('name', name),
                address=data.get('address', receipt.address),
                city=data.get('city', city),
                cuisine=data.get('cuisine', []),
                rating=data.get('rating'),
                user_ratings_total=data.get('user_ratings_total'),
                phone_number=data.get('phone_number'),
            )
            logger.info(f"Created new restaurant '{name}' with place_id {data['place_id']}")

        else:
            # Update restaurant data if needed
            data = fetch_restaurant_details_from_google(name, city)
            if data and data.get('place_id') != restaurant.place_id:
                restaurant.place_id = data.get('place_id', restaurant.place_id)
                restaurant.address = data.get('address', restaurant.address)
                restaurant.cuisine = data.get('cuisine', restaurant.cuisine)
                restaurant.rating = data.get('rating', restaurant.rating)
                restaurant.user_ratings_total = data.get('user_ratings_total', restaurant.user_ratings_total)
                restaurant.phone_number = data.get('phone_number', restaurant.phone_number)
                restaurant.save()
                logger.info(f"Updated restaurant '{name}' with new Google Places data")

        # Update user-restaurant interaction stats
        update_user_interaction(receipt.user, restaurant, receipt.date, receipt.price)

    except Receipt.DoesNotExist:
        logger.error(f"Receipt {receipt_id} not found")


def update_user_interaction(user, restaurant, date, price):
    with transaction.atomic():
        obj, created = UserRestaurantInteraction.objects.get_or_create(
            user=user,
            restaurant=restaurant,
            defaults={'visits': 1, 'last_visited': date, 'average_spend': price}
        )
        if not created:
            obj.visits += 1
            obj.last_visited = max(obj.last_visited, date)
            if obj.average_spend is None:
                obj.average_spend = price
            else:
                obj.average_spend = ((obj.average_spend * (obj.visits - 1)) + price) / obj.visits
            obj.save()
        logger.info(f"{'Created' if created else 'Updated'} UserRestaurantInteraction for user {user.id} and restaurant {restaurant.name}")
