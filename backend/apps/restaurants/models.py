from django.db import models

class Restaurant(models.Model):
    place_id = models.CharField(max_length=255, unique=True)
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

    def clean(self):
        super().clean()
