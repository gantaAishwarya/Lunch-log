from django.urls import path,include
from backend.apps.users.views import SignupView, LoginView, GetCSRFToken

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path('csrf/', GetCSRFToken.as_view(), name='get-csrf-token'),
    path("receipts/", include("backend.apps.receipts.urls")),

]
