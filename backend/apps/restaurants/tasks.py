from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_restaurant_data_for_city(city):
    from backend.apps.restaurants.services import fetch_restaurants_by_city
    try:
        logger.info(f"Fetching restaurant data for city: {city}")
        fetch_restaurants_by_city(city)
        return {"status": "success", "city": city}
    except Exception as e:
        return {"status": "error", "error": str(e)}
