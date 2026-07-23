import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings


def get_weather(city):
    """Fetch real weather from OpenWeatherMap"""
    try:
        api_key = settings.OPENWEATHER_API_KEY
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code == 200:
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'] * 3.6),
                'visibility': round(data.get('visibility', 0) / 1000),
                'pressure': data['main']['pressure'],
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon'],
                'success': True
            }
        else:
            return {'success': False, 'error': 'City not found'}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_forecast(city):
    """Get 5-day forecast"""
    try:
        api_key = '7ca0346c489123621f1236b94291f5f5'
        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',
            'cnt': 5
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code == 200:
            forecasts = []
            for item in data['list'][:5]:
                forecasts.append({
                    'time': item['dt_txt'],
                    'temp': round(item['main']['temp']),
                    'description': item['weather'][0]['description'].title(),
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity'],
                })
            return {'success': True, 'forecasts': forecasts}
        return {'success': False}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@login_required(login_url='/users/login/')
def weather_page(request):
    city = request.GET.get('city', 'Delhi')
    weather = get_weather(city)
    forecast = get_forecast(city) if weather['success'] else {'success': False}
    popular_cities = ["Delhi","Mumbai","Goa","Manali","Paris","Dubai","Tokyo","Bali"]
    return render(request, 'weather/weather.html', {
        'weather': weather,
        'forecast': forecast,
        'city': city,
        'city_list': popular_cities,
    })


@login_required(login_url='/users/login/')
def weather_api(request):
    """JSON endpoint for chatbot integration"""
    city = request.GET.get('city', 'Delhi')
    weather = get_weather(city)
    return JsonResponse(weather)