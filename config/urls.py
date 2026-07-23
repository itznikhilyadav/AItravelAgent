from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path(
        "chatbot/",
        include("chatbot.urls", namespace="chatbot")
    ),
    path("recommendation/", include("recommendation.urls")),
    path('booking/', include('booking.urls', namespace='booking')),
    path('itinerary/', include('itinerary.urls', namespace='itinerary')),
    path('weather/', include('weather.urls', namespace='weather')),
    
]