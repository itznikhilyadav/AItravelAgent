from django.urls import path
from . import views
from . import agent_views


app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('agent/', agent_views.agent_home, name='agent_home'),
    path('agent/plan/', agent_views.agent_plan, name='agent_plan'),
]