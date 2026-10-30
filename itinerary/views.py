from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from groq import Groq
from .models import Itinerary
import json
import os
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)




def generate_itinerary_ai(destination, start_date, duration, travellers, budget, style, interests):
    interests_str = ', '.join(interests) if interests else 'general sightseeing'

    prompt = f"""You are an expert travel planner. Create a detailed day-by-day itinerary.

Trip Details:
- Destination: {destination}
- Start date: {start_date}
- Duration: {duration} days
- Travellers: {travellers}
- Budget: {budget}
- Travel style: {style}
- Interests: {interests_str}

Return ONLY a valid JSON object. No markdown, no explanation, just raw JSON.

Format:
{{
  "trip_title": "5-Day Manali Adventure",
  "destination": "{destination}",
  "duration": {duration},
  "travellers": "{travellers}",
  "budget_type": "{budget}",
  "summary": "One sentence trip summary",
  "budget_breakdown": {{
    "hotels": "$350",
    "food": "$120",
    "activities": "$180",
    "transport": "$95",
    "total": "$745"
  }},
  "tips": ["Tip 1", "Tip 2", "Tip 3"],
  "days": [
    {{
      "day": 1,
      "title": "Arrival & City Exploration",
      "theme": "Getting settled and exploring",
      "activities": [
        {{
          "time": "10:00 AM",
          "title": "Activity name",
          "description": "2 sentence description with practical tips",
          "category": "sightseeing",
          "duration": "2 hours",
          "cost": "$10",
          "map_url": "https://maps.google.com/?q=activity+name+{destination}",
          "tags": ["Culture", "Must-see"]
        }}
      ]
    }}
  ]
}}

Rules:
- Create exactly {duration} days
- Each day must have 4-6 activities
- Categories: hotel, sightseeing, food, transport, adventure, shopping, culture, nature, nightlife
- Give REAL place names that exist in {destination}
- Make timings realistic with travel time
- Budget must match {budget}
- Return ONLY the JSON object"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a travel planning API. "
                    "Return only a valid JSON object. "
                    "Do not include markdown or explanations."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=4000,
        temperature=0.7,
        response_format={"type": "json_object"},
        reasoning_format="hidden",
    )

    message = completion.choices[0].message
    response = message.content

    if not response or not response.strip():
        raise ValueError(
            f"Groq returned an empty response. "
            f"Finish reason: {completion.choices[0].finish_reason}"
        )

    try:
        data = json.loads(response)

    except json.JSONDecodeError as e:
        start = max(0, e.pos - 300)
        end = min(len(response), e.pos + 300)

        error_context = response[start:end]

        print("\n========== ITINERARY JSON ERROR ==========")
        print("Error:", str(e))
        print("Line:", e.lineno)
        print("Column:", e.colno)
        print("Position:", e.pos)
        print("Response near error:")
        print(error_context)
        print("==========================================\n")

        raise ValueError(
            f"Invalid JSON at line {e.lineno}, "
            f"column {e.colno}. "
            f"Details: {error_context}"
        ) from e

    return data


@login_required(login_url='/users/login/')
def itinerary_home(request):
    my_itineraries = Itinerary.objects.filter(user=request.user)
    return render(request, 'itinerary/home.html', {'itineraries': my_itineraries})


@login_required(login_url='/users/login/')
def create_itinerary(request):
    if request.method == 'POST':
        destination = request.POST.get('destination', '')
        start_date = request.POST.get('start_date', '')
        duration = int(request.POST.get('duration', 5))
        travellers = request.POST.get('travellers', 'Couple')
        budget = request.POST.get('budget', 'Mid-range')
        style = request.POST.get('style', 'Balanced')
        interests = request.POST.getlist('interests')

        try:
            data = generate_itinerary_ai(
                destination, start_date, duration,
                travellers, budget, style, interests
            )
            itinerary = Itinerary.objects.create(
                user=request.user,
                destination=destination,
                start_date=start_date,
                duration_days=duration,
                travellers=travellers,
                budget=budget,
                travel_style=style,
                interests=interests,
                itinerary_data=data,
            )
            return redirect('itinerary:detail', pk=itinerary.pk)
        except Exception as e:
            return render(request, 'itinerary/create.html', {
                'error': f'Failed to generate itinerary: {str(e)}'
            })

    return render(request, 'itinerary/create.html', {'interests': INTERESTS})


@login_required(login_url='/users/login/')
def itinerary_detail(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, user=request.user)
    return render(request, 'itinerary/detail.html', {'itinerary': itinerary})


@login_required(login_url='/users/login/')
def delete_itinerary(request, pk):
    itinerary = get_object_or_404(Itinerary, pk=pk, user=request.user)
    itinerary.delete()
    return redirect('itinerary:home')

INTERESTS = [
    "Adventure",
    "Food & cuisine",
    "Culture & history",
    "Photography",
    "Wellness & spa",
    "Shopping",
    "Nature & trekking",
    "Nightlife",
    "Beaches",
    "Museums",
    "Religious sites",
    "Wildlife",
]


# NOTE:
# The file originally defined create_itinerary() twice.
# The POST-capable implementation above should be the only one.
# The duplicate form-only version has been removed to prevent overwriting.

