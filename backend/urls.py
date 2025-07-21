from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('backend.apps.users.urls')), 
    path('receipts/', include('backend.apps.receipts.urls')), 
]
