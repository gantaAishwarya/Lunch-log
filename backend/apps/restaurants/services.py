import requests
from django.conf import settings
from .models import Restaurant, UserRestaurantInteraction
from django.db.models import Sum

def fetch_restaurant_details_from_google(name, city):
    query = f"{name}, {city}"
    api_key = settings.GOOGLE_API_KEY

    find_url = settings.GOOGLE_PLACES_TEXT_SEARCH_URL
    find_params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id",
        "key": api_key
    }
    res = requests.get(find_url, params=find_params)
    if res.status_code != 200:
        return None

    candidates = res.json().get("candidates", [])
    if not candidates:
        return None

    place_id = candidates[0]["place_id"]

    detail_url = settings.GOOGLE_PLACES_DETAILS_URL
    detail_params = {
        "place_id": place_id,
        "fields": "place_id,name,formatted_address,formatted_phone_number,rating,user_ratings_total,type",
        "key": api_key
    }
    detail_res = requests.get(detail_url, params=detail_params)
    if detail_res.status_code != 200:
        return None

    result = detail_res.json().get("result")
    if not result:
        return None

    return {
        "place_id": result.get("place_id"),
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "city": city,
        "cuisine": result.get("types", []),
        "rating": result.get("rating"),
        "user_ratings_total": result.get("user_ratings_total"),
        "phone_number": result.get("formatted_phone_number")
    }

def get_recommendations_for_user(user, city: str, limit=10):
    print(f"Getting recommendations for user {user.id} in city '{city}'")

    # Restaurants the user has visited in this city
    user_visits_in_city = UserRestaurantInteraction.objects.filter(
        user=user,
        restaurant__city__iexact=city
    ).values('restaurant').annotate(
        total_visits=Sum('visits')
    ).order_by('-total_visits')

    visited_ids = [entry['restaurant'] for entry in user_visits_in_city]
    print(f"User visited restaurant IDs in city '{city}': {visited_ids}")

    # Exclude already visited restaurants for recommendation
    exclude_ids = set(visited_ids)

    # Find other popular restaurants in the city by all users, excluding user's visited ones
    popular_restaurants = UserRestaurantInteraction.objects.filter(
        restaurant__city__iexact=city
    ).exclude(
        restaurant__id__in=exclude_ids
    ).values('restaurant').annotate(
        total_visits=Sum('visits')
    ).order_by('-total_visits')[:limit]

    popular_ids = [entry['restaurant'] for entry in popular_restaurants]
    print(f"Popular restaurant IDs (excluding user's visited): {popular_ids}")

    # Combine: first user's visited restaurants ordered by visits, then popular restaurants
    combined_ids = visited_ids + popular_ids

    # If no restaurants to recommend, fallback to top-rated restaurants in the city
    if not combined_ids:
        fallback_restaurants = list(Restaurant.objects.filter(city__iexact=city).order_by('-rating')[:limit])
        print(f"Fallback to top rated restaurants (including visited): {[r.name for r in fallback_restaurants]}")
        return fallback_restaurants

    # Fetch Restaurant objects preserving the order in combined_ids
    restaurants = list(Restaurant.objects.filter(id__in=combined_ids))
    restaurants.sort(key=lambda r: combined_ids.index(r.id))

    print(f"Final recommended restaurants: {[r.name for r in restaurants[:limit]]}")

    return restaurants[:limit]