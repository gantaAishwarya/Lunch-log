from django.urls import path
from .views import GooglePlacesFetchView

urlpatterns = [
    path("fetch-restaurant/", GooglePlacesFetchView.as_view(), name="fetch-restaurant"),
]
