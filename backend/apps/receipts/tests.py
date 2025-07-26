import pytest
from io import BytesIO
from datetime import date, timedelta
from PIL import Image
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.receipts.models import Receipt

User = get_user_model()

def generate_image_file():
    image = Image.new("RGB", (100, 100), color="red")
    tmp_file = BytesIO()
    image.save(tmp_file, format="JPEG")
    tmp_file.seek(0)
    return SimpleUploadedFile("test.jpg", tmp_file.read(), content_type="image/jpeg")

class TestReceiptAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            full_name="Test User"
        )
        self.client.force_authenticate(user=self.user)
        self.receipt_url = reverse("receipt-list")

        Receipt.objects.all().delete()

    def create_receipt(self, **kwargs):
        data = {
            "date": kwargs.get("date", date.today()),
            "price": kwargs.get("price", "10.00"),
            "restaurant_name": kwargs.get("restaurant_name", "Test Restaurant"),
            "address": kwargs.get("address", "123 Test Street"),
            "image": kwargs.get("image", generate_image_file()),
        }
        return self.client.post(self.receipt_url, data, format="multipart")

    def test_create_receipt_success(self):
        response = self.create_receipt()
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["restaurant_name"] == "Test Restaurant"

    def test_create_receipt_future_date(self):
        future_date = date.today() + timedelta(days=1)
        response = self.create_receipt(date=future_date)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "date" in response.data

    def test_create_receipt_negative_price(self):
        response = self.create_receipt(price="-5.00")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "price" in response.data

    def test_list_user_receipts(self):
        self.create_receipt()
        self.create_receipt(restaurant_name="Another One")
        response = self.client.get(self.receipt_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert len(response.data['results']) == 2

    def test_filter_receipts_by_month_valid(self):
        Receipt.objects.all().delete()

        Receipt.objects.create(
            user=self.user,
            image=generate_image_file(),
            date=date(2024, 7, 15),
            price="12.00",
            restaurant_name="July Diner",
            address="Some Address",
        )
        Receipt.objects.create(
            user=self.user,
            image=generate_image_file(),
            date=date(2024, 6, 10),
            price="15.00",
            restaurant_name="June Grill",
            address="Another Address",
        )
        response = self.client.get(self.receipt_url + "?month=2024-07")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert len(response.data['results']) == 1

    def test_filter_receipts_invalid_month_format(self):
        response = self.client.get(self.receipt_url + "?month=07-2024")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_receipt(self):
        post_response = self.create_receipt()
        receipt_id = post_response.data["id"]
        update_url = reverse("receipt-detail", args=[receipt_id])
        response = self.client.patch(update_url, {"price": "20.00"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["price"] == "20.00"

    def test_delete_receipt(self):
        post_response = self.create_receipt()
        receipt_id = post_response.data["id"]
        delete_url = reverse("receipt-detail", args=[receipt_id])
        response = self.client.delete(delete_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Receipt.objects.filter(id=receipt_id).exists()

    def test_cannot_access_other_user_receipt(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="pass",
            full_name="Other User"
        )
        receipt = Receipt.objects.create(
            user=other_user,
            image=generate_image_file(),
            date=date.today(),
            price="25.00",
            restaurant_name="Secret Spot",
            address="Hidden Address",
        )
        detail_url = reverse("receipt-detail", args=[receipt.id])
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
