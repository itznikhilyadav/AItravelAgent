from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime

from .forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_superuser(request):
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin@12345"
        )
        return HttpResponse("Superuser created!")

    return HttpResponse("Superuser already exists.")


# ===========================
# User Registration
# ===========================
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("dashboard")
        else:
            print(form.errors)          # Add this
            messages.error(request, form.errors)   # Add this

    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


# ===========================
# User Login
# ===========================
def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


# ===========================
# User Logout
# ===========================
@login_required(login_url="login")
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")





# ===========================
# Dashboard
# ===========================
@login_required(login_url="login")
def dashboard(request):
    try:
        from chatbot.models import ChatHistory
        recent_chats = ChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:3]
        chat_count = ChatHistory.objects.filter(user=request.user).count()
    except Exception:
        recent_chats = []
        chat_count = 0

    try:
        from itinerary.models import Itinerary
        itineraries = Itinerary.objects.filter(
            user=request.user
        ).order_by('-created_at')[:3]
        trip_count = Itinerary.objects.filter(user=request.user).count()
        upcoming_trip = Itinerary.objects.filter(
            user=request.user,
            start_date__gte=datetime.date.today()
        ).order_by('start_date').first()
    except Exception:
        itineraries = []
        trip_count = 0
        upcoming_trip = None

    try:
        from recommendation.models import SavedDestination
        saved_destinations = SavedDestination.objects.filter(
            user=request.user
        ).order_by('-saved_at')[:3]
        dest_count = SavedDestination.objects.filter(user=request.user).count()
        country_count = SavedDestination.objects.filter(
            user=request.user
        ).values('country').distinct().count()
    except Exception:
        saved_destinations = []
        dest_count = 0
        country_count = 0

    stats = {
        'trips': trip_count,
        'destinations': dest_count,
        'chats': chat_count,
        'countries': country_count,
    }

    return render(request, "users/dashboard.html", {
        'itineraries': itineraries,
        'saved_destinations': saved_destinations,
        'recent_chats': recent_chats,
        'stats': stats,
        'upcoming_trip': upcoming_trip,
    })