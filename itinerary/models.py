from django.db import models
from django.conf import settings

class Itinerary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.CharField(max_length=200)
    start_date = models.DateField()
    duration_days = models.IntegerField()
    travellers = models.CharField(max_length=100)
    budget = models.CharField(max_length=100)
    travel_style = models.CharField(max_length=100)
    interests = models.JSONField(default=list)
    itinerary_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.destination} ({self.duration_days} days)"

    class Meta:
        ordering = ['-created_at']