from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking_home, name='home'),
    path('flights/', views.flight_search, name='flight_search'),
    path('hotels/', views.hotel_search, name='hotel_search'),
]