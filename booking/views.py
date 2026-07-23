from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from groq import Groq
import json
from django.conf import settings
import os


client = Groq(api_key=settings.GROQ_API_KEY)



def get_flights_from_ai(origin, destination, date, passengers, travel_class):
    prompt = f"""You are a flight search expert. Give realistic flight options.

Search: {origin} to {destination}
Date: {date}
Passengers: {passengers}
Class: {travel_class}

Return ONLY a valid JSON array with exactly 5 flight options. No markdown, no explanation.
Format:
[
  {{
    "airline": "Air India",
    "airline_code": "AI",
    "flight_no": "AI-101",
    "departure_time": "06:30",
    "arrival_time": "09:45",
    "duration": "3h 15m",
    "stops": "Non-stop",
    "price": "$245",
    "class": "{travel_class}",
    "seats_left": 8,
    "features": ["Meal included", "USB charging", "Extra legroom"]
  }}
]

Rules:
- Give REAL airline names that actually fly this route
- Give REALISTIC prices for {travel_class} class
- Vary departure times across morning, afternoon, evening
- Mix non-stop and 1-stop options
- Return ONLY the JSON array"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a flight search API. Return ONLY valid JSON arrays. No markdown, no explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7,
    )

    response = completion.choices[0].message.content.strip()
    start = response.find('[')
    end = response.rfind(']') + 1
    if start != -1 and end > start:
        response = response[start:end]
    return json.loads(response)


def get_hotels_from_ai(city, check_in, check_out, guests, budget):
    prompt = f"""You are a hotel search expert. Give realistic hotel options.

City: {city}
Check-in: {check_in}
Check-out: {check_out}
Guests: {guests}
Budget: {budget}

Return ONLY a valid JSON array with exactly 6 hotel options. No markdown, no explanation.
Format:
[
  {{
    "name": "The Grand Hotel",
    "stars": 4,
    "area": "City Center",
    "address": "123 Main Street, {city}",
    "price_per_night": "$89",
    "total_price": "$445",
    "rating": 8.5,
    "reviews": 1243,
    "amenities": ["Free WiFi", "Swimming Pool", "Breakfast", "Gym"],
    "room_type": "Deluxe Double Room",
    "highlights": "Walking distance to main attractions",
    "map_url": "https://maps.google.com/?q=The+Grand+Hotel+{city}"
  }}
]

Rules:
- Give REAL hotel names that exist in {city}
- Match budget: {budget}
- Vary star ratings from 3 to 5 stars
- Give realistic prices per night
- Include actual amenities
- Return ONLY the JSON array"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a hotel search API. Return ONLY valid JSON arrays. No markdown, no explanation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    response = completion.choices[0].message.content.strip()
    start = response.find('[')
    end = response.rfind(']') + 1
    if start != -1 and end > start:
        response = response[start:end]
    return json.loads(response)


@login_required(login_url='/users/login/')
def booking_home(request):
    return render(request, 'booking/booking.html')


@login_required(login_url='/users/login/')
def flight_search(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        origin = data.get('origin', '')
        destination = data.get('destination', '')
        date = data.get('date', '')
        passengers = data.get('passengers', '1 Adult')
        travel_class = data.get('travel_class', 'Economy')

        if not origin or not destination or not date:
            return JsonResponse({'error': 'Please fill all fields'}, status=400)

        flights = get_flights_from_ai(origin, destination, date, passengers, travel_class)
        return JsonResponse({'flights': flights, 'status': 'success'})

    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'AI response error: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/users/login/')
def hotel_search(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        city = data.get('city', '')
        check_in = data.get('check_in', '')
        check_out = data.get('check_out', '')
        guests = data.get('guests', '1 Guest')
        budget = data.get('budget', 'Any budget')

        if not city or not check_in or not check_out:
            return JsonResponse({'error': 'Please fill all fields'}, status=400)

        hotels = get_hotels_from_ai(city, check_in, check_out, guests, budget)
        return JsonResponse({'hotels': hotels, 'status': 'success'})

    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'AI response error: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)