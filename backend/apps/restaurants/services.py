import requests
import time
from django.conf import settings
from .models import Restaurant

GOOGLE_PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def fetch_restaurants_by_city(city_name: str):
    """
    Fetches restaurants in the given city using Google Places Text Search API
    and stores details in the database.
    """
    params = {
        "query": f"restaurants in {city_name}",
        "key": settings.GOOGLE_API_KEY,
    }

    while True:
        response = requests.get(GOOGLE_PLACES_TEXT_SEARCH_URL, params=params)
        data = response.json()

        if data.get("status") != "OK":
            raise Exception(f"Google Places Text Search error: {data.get('status')}")

        for place in data.get("results", []):
            place_id = place.get("place_id")
            if place_id:
                fetch_and_store_restaurant_details(place_id, city=city_name)

        # Handle pagination
        next_page_token = data.get("next_page_token")
        if next_page_token:
            time.sleep(2)  # per Google API docs
            params["pagetoken"] = next_page_token
        else:
            break

def search_places_by_city(city_name: str, keyword: str = None, limit: int = 5) -> list:
    """
    Fetches restaurant places for a city using Google Places API (Text Search).
    This does NOT save to DB, only returns summary results for recommendations.
    """
    params = {
        "query": f"{keyword} food in {city_name}" if keyword else f"restaurants in {city_name}",
        "key": settings.GOOGLE_API_KEY,
    }

    response = requests.get(GOOGLE_PLACES_TEXT_SEARCH_URL, params=params)
    data = response.json()

    if data.get("status") != "OK":
        return []

    results = []
    for place in data.get("results", [])[:limit]:
        results.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "types": place.get("types", []),
        })

    return results


def fetch_and_store_restaurant_details(place_id: str, city: str = None):
    """
    Fetch detailed info of a restaurant by place_id and save it to the DB.
    """
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,types,rating,user_ratings_total,website,formatted_phone_number",
        "key": settings.GOOGLE_API_KEY,
    }

    response = requests.get(GOOGLE_PLACES_DETAILS_URL, params=params)
    data = response.json()

    if data.get("status") != "OK":
        raise Exception(f"Google Places Details API error: {data.get('status')}")

    result = data.get("result", {})

    restaurant, created = Restaurant.objects.update_or_create(
        place_id=place_id,
        defaults={
            "name": result.get("name"),
            "address": result.get("formatted_address"),
            "city": city,
            "cuisine": result.get("types", []),
            "rating": result.get("rating"),
            "user_ratings_total": result.get("user_ratings_total"),
            "phone_number": result.get("formatted_phone_number"),
        }
    )
    return restaurant

