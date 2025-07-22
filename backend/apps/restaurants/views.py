from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import fetch_restaurants_by_city
    
class GooglePlacesFetchView(APIView):
    """
    Fetches and stores restaurant details by city using Google Places API.
    """
    def post(self, request):
        city = request.data.get("city")
        if not city:
            return Response({"error": "city is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fetch_restaurants_by_city(city)
            return Response({"message": f"Restaurant data fetched for {city}"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
