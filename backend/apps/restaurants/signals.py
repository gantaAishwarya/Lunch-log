from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.apps.receipts.models import Receipt
from backend.apps.restaurants.tasks import fetch_and_create_restaurant_from_receipt

@receiver(post_save, sender=Receipt)
def handle_receipt_creation(sender, instance, created, **kwargs):
    if not created:
        return
    fetch_and_create_restaurant_from_receipt.delay(instance.id)
