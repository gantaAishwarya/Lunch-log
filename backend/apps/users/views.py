from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login
from django.contrib.auth import get_user_model,authenticate
from .serializers import SignupSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view

User = get_user_model()

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user = authenticate(request, email=user.email, password=request.data['password'])
            if user:
                login(request, user)
                return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Authentication failed after signup"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@ensure_csrf_cookie
def set_csrf_token(request):
    return Response({'message': 'CSRF cookie set'})