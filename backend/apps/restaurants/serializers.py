from rest_framework import serializers
from .models import Restaurant

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id',
            'place_id',
            'name',
            'address',
            'city',
            'cuisine',
            'rating',
            'user_ratings_total',
            'phone_number',
        ]
