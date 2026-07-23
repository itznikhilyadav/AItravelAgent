from django.urls import path
from itinerary import views

app_name = 'itinerary'

urlpatterns = [
    path('', views.itinerary_home, name='home'),
    path('create/', views.create_itinerary, name='create'),
    path('<int:pk>/', views.itinerary_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_itinerary, name='delete'),
]