from django.db import models
from django.conf import settings
from django.conf import settings
from backend.apps.receipts.utils import storage, user_receipt_upload_path

class Receipt(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receipts")
    image = models.ImageField(upload_to=user_receipt_upload_path,storage=storage)
    date = models.DateField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    restaurant_name = models.CharField(max_length=255, null=False, blank=False)
    address = models.TextField(null=False, blank=False)

    class Meta:
        ordering = ['-date', 'restaurant_name']
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"

    def __str__(self):
        return f"{self.restaurant_name} - {self.date}"
    
    def clean(self):
        super().clean()
