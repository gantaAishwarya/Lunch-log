from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import Counter
from backend.apps.restaurants.models import Restaurant
from backend.apps.restaurants.services import fetch_restaurants_by_city, search_places_by_city

class FoodRecommendationView(APIView):
    def get(self, request):
        city = request.query_params.get("city")
        if not city:
            return Response({"error": "City is required"}, status=status.HTTP_400_BAD_REQUEST)

        stored_restaurants = Restaurant.objects.filter(city__iexact=city)

        if not stored_restaurants.exists():
            try:
                fetch_restaurants_by_city(city)  # This populates the DB
                stored_restaurants = Restaurant.objects.filter(city__iexact=city)
                if not stored_restaurants.exists():
                    return Response({"message": f"No restaurants found for {city} after fetching."}, status=404)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        all_cuisines = []
        for r in stored_restaurants:
            all_cuisines.extend([c.lower() for c in r.cuisine])
        top_cuisines = [c for c, _ in Counter(all_cuisines).most_common(3)]

        google_recommendations = []
        for cuisine in top_cuisines:
            google_recommendations.extend(search_places_by_city(city, keyword=cuisine, limit=2))

        response_data = {
            "city": city,
            "top_cuisines": top_cuisines,
            "local_restaurants": [
                {
                    "name": r.name,
                    "cuisine": r.cuisine,
                    "address": r.address,
                    "rating": r.rating,
                } for r in stored_restaurants[:5]
            ],
            "google_recommendations": google_recommendations
        }

        return Response(response_data, status=status.HTTP_200_OK)
