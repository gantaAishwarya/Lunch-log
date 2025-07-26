from django.db import models
from django.conf import settings

class Restaurant(models.Model):
    place_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    cuisine = models.JSONField(default=list)
    rating = models.FloatField(null=True, blank=True)
    user_ratings_total = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({', '.join(self.cuisine)})" if self.cuisine else self.name

    class Meta:
        ordering = ['-rating']
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

class UserRestaurantInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    
    visits = models.PositiveIntegerField(default=1)
    last_visited = models.DateField()
    average_spend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("user", "restaurant")
        ordering = ['-last_visited']