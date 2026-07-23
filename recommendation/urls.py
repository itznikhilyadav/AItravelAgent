from django.urls import path
from . import views
app_name = "recommendation"

urlpatterns = [
    path('', views.recommend_view, name='recommendation'),
    path('preferences/', views.recommend_view, name='preference_setup'),
    path('save/', views.save_destination, name='save_destination'),
]