from rest_framework import serializers
from .models import Receipt
from backend.apps.receipts.utils import storage
from datetime import date as dt_date

class ReceiptSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Receipt
        fields = ['id', 'user', 'date', 'price', 'restaurant_name', 'address', 'image', 'image_url']
        read_only_fields = ['user', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = storage.url(obj.image.name)
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive.")
        return value

    def validate_date(self, value):
        if value > dt_date.today():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value
