from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/auth/', include('backend.apps.users.urls')), 
    path('api/receipts/', include('backend.apps.receipts.urls')), 
    path("api/recommendations/", include("backend.apps.restaurants.urls")),
]
