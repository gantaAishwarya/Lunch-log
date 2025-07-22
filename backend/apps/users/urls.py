from django.urls import path,include
from backend.apps.users.views import SignupView, LoginView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
]
