from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import datetime
from .models import Receipt
from .serializers import ReceiptSerializer

class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Receipt.objects.filter(user=self.request.user)
        month = self.request.query_params.get("month")

        if month:
            try:
                dt = datetime.strptime(month, "%Y-%m")
                queryset = queryset.filter(date__year=dt.year, date__month=dt.month)
            except ValueError:
                raise ValidationError({"month": "Invalid month format. Use YYYY-MM."})

        return queryset

    def get_serializer_context(self):
        # Pass request to serializer for building absolute URLs
        return {'request': self.request}

    def perform_create(self, serializer):
        # Ensure user is set from request (ignore user field from client)
        serializer.save(user=self.request.user)
