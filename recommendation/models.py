from django.db import models
from django.conf import settings

class UserPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip_type = models.CharField(max_length=50)
    climate = models.CharField(max_length=50)
    budget_per_day = models.IntegerField(default=100)
    duration_days = models.IntegerField(default=7)
    activities = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.trip_type}"

class SavedDestination(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    match_score = models.IntegerField()
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.destination_name}"