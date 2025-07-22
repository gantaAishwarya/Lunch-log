from django.urls import path
from .views import FoodRecommendationView

urlpatterns = [
    path('', FoodRecommendationView.as_view(), name='food_recommendations'),
]