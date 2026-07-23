import json
import logging
from groq import Groq
from django.conf import settings

import os


client = Groq(api_key=settings.GROQ_API_KEY)

logger = logging.getLogger(__name__)




def get_recommendations(trip_type, climate, budget, duration, activities):
    print(f"DEBUG - Calling Groq API...")
    print(f"DEBUG - Trip: {trip_type}, Climate: {climate}, Budget: ${budget}, Duration: {duration} days")
    print(f"DEBUG - Activities: {activities}")

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        activities_str = ', '.join(activities) if activities else 'general sightseeing'

        prompt = f"""You are a travel recommendation expert. Based on these preferences, recommend exactly 6 destinations.

User Preferences:
- Trip type: {trip_type}
- Climate preference: {climate}
- Budget per day: ${budget} USD
- Trip duration: {duration} days
- Favourite activities: {activities_str}

Return ONLY a valid JSON array with exactly 6 destinations.
No explanation, no markdown, no extra text, no code blocks.
Just raw JSON starting with [ and ending with ]

Each destination must follow this exact format:
[
  {{
    "name": "City or Country name",
    "country": "Country or Region",
    "emoji": "single emoji",
    "description": "Two sentences explaining why this matches their preferences.",
    "tags": ["Tag1", "Tag2", "Tag3", "Tag4"],
    "scores": {{
      "match": 95,
      "value": 88,
      "weather": 90,
      "activities": 92
    }},
    "budget_range": "$50-100/day",
    "best_time": "April - October",
    "highlights": ["Top sight 1", "Top sight 2", "Top sight 3"]
  }}
]

Important rules:
- All score values must be integers between 60 and 99
- Sort destinations by match score from highest to lowest
- Budget under $60/day: recommend Vietnam, Nepal, India, Cambodia, Bolivia, Georgia
- Budget $60-150/day: recommend Thailand, Bali, Portugal, Mexico, Morocco, Colombia
- Budget $151-300/day: recommend Japan, Spain, Greece, Croatia, Costa Rica, South Africa
- Budget over $300/day: recommend Maldives, Switzerland, Iceland, New Zealand, Norway, Dubai
- Each recommendation must be DIFFERENT and unique
- Vary the continents do not recommend 6 from the same region
- Return ONLY the JSON array with no other text"""

        print("DEBUG - Sending request to Groq...")

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a travel expert API. You respond ONLY with valid JSON arrays. Never include explanations, markdown formatting, or code blocks. Only raw JSON starting with [ and ending with ]."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2500,
            temperature=0.8,
        )

        response_text = completion.choices[0].message.content.strip()
        print(f"DEBUG - Groq responded with {len(response_text)} characters")
        print(f"DEBUG - First 300 chars: {response_text[:300]}")

        # Clean markdown if AI adds it
        if '```' in response_text:
            parts = response_text.split('```')
            for part in parts:
                part = part.strip()
                if part.startswith('json'):
                    part = part[4:].strip()
                if part.startswith('['):
                    response_text = part
                    break

        # Extract JSON array
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

        print("DEBUG - Parsing JSON...")
        destinations = json.loads(response_text)
        print(f"DEBUG - Successfully got {len(destinations)} destinations!")

        # Validate each destination
        validated = []
        for dest in destinations:
            if 'name' not in dest:
                continue

            if 'scores' not in dest:
                dest['scores'] = {
                    'match': 80,
                    'value': 75,
                    'weather': 78,
                    'activities': 76
                }

            for key in ['match', 'value', 'weather', 'activities']:
                if key not in dest['scores']:
                    dest['scores'][key] = 75
                dest['scores'][key] = max(60, min(99, int(dest['scores'][key])))

            if 'tags' not in dest or not dest['tags']:
                dest['tags'] = ['Travel', 'Explore', 'Adventure']

            if 'highlights' not in dest or not dest['highlights']:
                dest['highlights'] = ['Amazing scenery', 'Great food', 'Rich culture']

            if 'description' not in dest:
                dest['description'] = 'A wonderful destination that matches your travel preferences.'

            if 'emoji' not in dest or not dest['emoji']:
                dest['emoji'] = '✈️'

            if 'budget_range' not in dest:
                dest['budget_range'] = f'~${budget}/day'

            if 'best_time' not in dest:
                dest['best_time'] = 'Year round'

            if 'country' not in dest:
                dest['country'] = dest['name']

            validated.append(dest)

        print(f"DEBUG - Returning {len(validated[:6])} validated destinations")
        return validated[:6]

    except json.JSONDecodeError as e:
        print(f"JSON PARSE ERROR: {e}")
        return get_fallback_recommendations(trip_type, budget)

    except Exception as e:
        print(f"GROQ API ERROR: {type(e).__name__}: {e}")
        return get_fallback_recommendations(trip_type, budget)


def get_fallback_recommendations(trip_type, budget):
    print("DEBUG - Using fallback recommendations")
    return [
        {
            'name': 'Bali',
            'country': 'Indonesia',
            'emoji': '🌴',
            'description': 'Tropical paradise with stunning temples, rice terraces and world-class surf beaches. Perfect for most travel styles and budgets.',
            'tags': ['Beach', 'Culture', 'Food', 'Temples'],
            'scores': {'match': 88, 'value': 90, 'weather': 92, 'activities': 85},
            'budget_range': '$40-120/day',
            'best_time': 'April - October',
            'highlights': ['Tanah Lot Temple', 'Ubud Rice Terraces', 'Seminyak Beach'],
        },
        {
            'name': 'Thailand',
            'country': 'Southeast Asia',
            'emoji': '🏯',
            'description': 'Vibrant street food scene, stunning islands and rich culture. Exceptional value for money with something for every traveller.',
            'tags': ['Budget', 'Food', 'Beach', 'Culture'],
            'scores': {'match': 85, 'value': 95, 'weather': 88, 'activities': 82},
            'budget_range': '$30-100/day',
            'best_time': 'November - April',
            'highlights': ['Chiang Mai Temples', 'Phi Phi Islands', 'Bangkok Street Food'],
        },
        {
            'name': 'Portugal',
            'country': 'Europe',
            'emoji': '🏰',
            'description': "Europe's sunniest destination with great food and stunning coastlines. A hidden gem in Western Europe.",
            'tags': ['Culture', 'Coast', 'History', 'Food'],
            'scores': {'match': 82, 'value': 80, 'weather': 85, 'activities': 80},
            'budget_range': '$60-150/day',
            'best_time': 'March - October',
            'highlights': ['Lisbon Old Town', 'Algarve Beaches', 'Douro Valley Wine'],
        },
        {
            'name': 'Japan',
            'country': 'East Asia',
            'emoji': '⛩️',
            'description': 'Unique blend of ancient tradition and futuristic technology with incredible food culture.',
            'tags': ['Culture', 'Food', 'Tech', 'History'],
            'scores': {'match': 79, 'value': 72, 'weather': 80, 'activities': 88},
            'budget_range': '$80-200/day',
            'best_time': 'March - May, Oct - Nov',
            'highlights': ['Mount Fuji', 'Tokyo Shibuya', 'Kyoto Temples'],
        },
        {
            'name': 'Vietnam',
            'country': 'Southeast Asia',
            'emoji': '🛖',
            'description': 'Stunning landscapes from Ha Long Bay to rice terraces with incredible street food at affordable prices.',
            'tags': ['Budget', 'Food', 'Culture', 'Nature'],
            'scores': {'match': 76, 'value': 92, 'weather': 75, 'activities': 80},
            'budget_range': '$25-80/day',
            'best_time': 'February - April',
            'highlights': ['Ha Long Bay', 'Hoi An Old Town', 'Hanoi Street Food'],
        },
        {
            'name': 'Morocco',
            'country': 'North Africa',
            'emoji': '🕌',
            'description': 'Ancient medinas, Sahara desert adventures and vibrant souks create an unforgettable experience.',
            'tags': ['Culture', 'Desert', 'Adventure', 'History'],
            'scores': {'match': 74, 'value': 85, 'weather': 78, 'activities': 82},
            'budget_range': '$40-120/day',
            'best_time': 'March - May, Sept - Nov',
            'highlights': ['Sahara Desert', 'Marrakech Medina', 'Chefchaouen Blue City'],
        },
    ]