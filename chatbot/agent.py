from groq import Groq
import json

GROQ_API_KEY = 'REMOVED_SECRET'
client = Groq(api_key=GROQ_API_KEY)


def run_agent(goal: str) -> dict:
    """
    True Agentic AI — takes one goal and completes 8 tasks automatically
    """

    prompt = f"""You are an Agentic AI Travel Planner. The user has given you ONE goal.
Your job is to automatically complete ALL 8 tasks and return a complete travel plan.

User goal: "{goal}"

Complete ALL these tasks automatically:
1. Analyse the budget, destination, duration, and travel dates from the goal
2. Check weather for that destination and month
3. Find the best flight options with prices
4. Search hotels within budget
5. Build a complete day-by-day itinerary
6. Recommend top restaurants for each day
7. Save the trip summary
8. Prepare modification suggestions

Return ONLY a valid JSON object. No markdown, no explanation.

{{
  "goal_analysis": {{
    "destination": "Goa",
    "duration_days": 5,
    "total_budget": "₹25,000",
    "travel_month": "August 2026",
    "travellers": 1,
    "budget_per_day": "₹5,000"
  }},
  "weather": {{
    "temperature": "28°C",
    "condition": "Partly cloudy with occasional showers",
    "tip": "Pack light clothes and a raincoat",
    "best_time_of_day": "Mornings are best for beach visits"
  }},
  "flights": [
    {{
      "airline": "IndiGo",
      "flight_no": "6E-441",
      "route": "DEL → GOI",
      "departure": "06:00",
      "arrival": "08:15",
      "price": "₹3,600 return",
      "tip": "Book 3 weeks early for best price"
    }}
  ],
  "hotels": [
    {{
      "name": "Hotel Baga Residency",
      "area": "Baga Beach, North Goa",
      "stars": 3,
      "price_per_night": "₹1,800",
      "total": "₹7,200 for 4 nights",
      "amenities": ["Free WiFi", "Breakfast", "AC", "Pool"],
      "map_url": "https://maps.google.com/?q=Hotel+Baga+Residency+Goa"
    }}
  ],
  "itinerary": [
    {{
      "day": 1,
      "title": "Arrival and Baga Beach",
      "activities": [
        {{"time": "09:00", "activity": "Arrive at Goa airport, check in to hotel", "cost": "₹0"}},
        {{"time": "12:00", "activity": "Lunch at Britto's restaurant on Baga Beach", "cost": "₹400"}},
        {{"time": "15:00", "activity": "Baga Beach — water sports, parasailing", "cost": "₹800"}},
        {{"time": "19:00", "activity": "Sunset at Calangute Beach", "cost": "₹0"}},
        {{"time": "20:30", "activity": "Dinner at a beach shack", "cost": "₹500"}}
      ]
    }}
  ],
  "restaurants": [
    {{
      "name": "Britto's",
      "area": "Baga Beach",
      "cuisine": "Seafood & Continental",
      "avg_cost": "₹400 per person",
      "must_try": "Prawn curry and Fish thali",
      "map_url": "https://maps.google.com/?q=Britto's+Baga+Goa"
    }}
  ],
  "budget_breakdown": {{
    "flights": "₹3,600",
    "hotels": "₹7,200",
    "food": "₹4,500",
    "activities": "₹3,000",
    "transport": "₹2,000",
    "shopping": "₹2,000",
    "total": "₹22,300",
    "remaining": "₹2,700"
  }},
  "modifications_available": [
    "Switch to a cheaper hotel to save ₹2,000",
    "Add a day trip to Dudhsagar Falls for ₹1,200",
    "Upgrade to 4-star hotel for ₹800 more per night",
    "Add scuba diving at Grande Island for ₹3,500"
  ],
  "trip_saved": true,
  "summary": "5-day Goa trip under ₹25,000 — flights, hotel, food and activities all planned!"
}}

Rules:
- Extract REAL destination, budget and duration from the goal
- Give REAL hotel names and restaurant names
- Make prices realistic and within the stated budget
- Create exactly the right number of itinerary days
- Return ONLY the JSON object"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an agentic travel planning API. Return ONLY valid JSON. No markdown, no explanation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7,
        )
        response = completion.choices[0].message.content.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            response = response[start:end]
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}