from rest_framework.routers import DefaultRouter
from .views import ReceiptViewSet
from django.urls import path, include

router = DefaultRouter()
router.register('', ReceiptViewSet, basename='receipt')

urlpatterns = [
    path('', include(router.urls)),
]
