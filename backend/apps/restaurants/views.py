from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import RestaurantSerializer
from .services import get_recommendations_for_user


class FoodRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response({"error": "City is required"}, status=status.HTTP_400_BAD_REQUEST)

        recommendations = get_recommendations_for_user(request.user, city.strip())
        serializer = RestaurantSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
