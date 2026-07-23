from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .ml_engine import get_recommendations
from .models import UserPreference, SavedDestination

TRIP_TYPES = [
    'Adventure', 'Beach & relaxation', 'Cultural & history',
    'Honeymoon', 'Budget backpacking', 'Family trip', 'Business + leisure',
]

CLIMATES = [
    'Tropical & warm', 'Cold & snowy', 'Mild & pleasant',
    'Desert & dry', 'Any climate',
]

ACTIVITIES = [
    'Surfing', 'Trekking', 'Food tour', 'Museums',
    'Nightlife', 'Photography', 'Shopping', 'Wellness', 'Diving',
]


@login_required(login_url='/users/login/')
def recommend_view(request):
    results = []
    preferences = None

    if request.method == 'POST':
        trip_type = request.POST.get('trip_type', 'Adventure')
        climate = request.POST.get('climate', 'Any climate')
        budget = int(request.POST.get('budget', 100))
        duration = int(request.POST.get('duration', 7))
        activities = request.POST.getlist('activities')

        UserPreference.objects.create(
            user=request.user,
            trip_type=trip_type,
            climate=climate,
            budget_per_day=budget,
            duration_days=duration,
            activities=activities,
        )

        results = get_recommendations(trip_type, climate, budget, duration, activities)
        preferences = {
            'trip_type': trip_type,
            'climate': climate,
            'budget': budget,
            'duration': duration,
            'activities': activities,
        }

    saved = SavedDestination.objects.filter(user=request.user).values_list('destination_name', flat=True)

    return render(request, 'recommendation/recommend.html', {
        'results': results,
        'preferences': preferences,
        'trip_types': TRIP_TYPES,
        'climates': CLIMATES,
        'activities': ACTIVITIES,
        'saved_destinations': list(saved),
    })


@login_required(login_url='/users/login/')
def save_destination(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        country = request.POST.get('country')
        score = request.POST.get('score', 0)
        SavedDestination.objects.get_or_create(
            user=request.user,
            destination_name=name,
            defaults={'country': country, 'match_score': score}
        )
    from django.shortcuts import redirect
    return redirect('recommendation:recommendation')