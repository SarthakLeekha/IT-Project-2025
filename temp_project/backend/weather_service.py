import requests
import os
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


WEATHER_API_KEY = '8d591758d7a04feca2894517250811'
WEATHER_BASE_URL = 'https://api.weatherapi.com/v1'


MOCK_WEATHER_DATA = {
    'Pune': {
        'temperature': 28.5,
        'humidity': 65,
        'pressure': 1013,
        'wind_speed': 12.5,
        'description': 'Partly cloudy',
        'icon': '02d',
        'rainfall': 0.0,
        'uv_index': 7.2
    },
    'Mumbai': {
        'temperature': 30.2,
        'humidity': 78,
        'pressure': 1010,
        'wind_speed': 15.3,
        'description': 'Clear sky',
        'icon': '01d',
        'rainfall': 0.0,
        'uv_index': 8.1
    },
    'Delhi': {
        'temperature': 32.1,
        'humidity': 45,
        'pressure': 1008,
        'wind_speed': 8.7,
        'description': 'Haze',
        'icon': '50d',
        'rainfall': 0.0,
        'uv_index': 6.8
    },
    'Bangalore': {
        'temperature': 26.8,
        'humidity': 72,
        'pressure': 1015,
        'wind_speed': 10.2,
        'description': 'Scattered clouds',
        'icon': '03d',
        'rainfall': 2.1,
        'uv_index': 9.3
    }
}

def get_coordinates(location):
    """Get latitude and longitude for a location using WeatherAPI.com"""
    try:
        if WEATHER_API_KEY == 'demo_key':
            
            mock_coords = {
                'Pune': {'lat': 18.5204, 'lon': 73.8567},
                'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
                'Delhi': {'lat': 28.7041, 'lon': 77.1025},
                'Bangalore': {'lat': 12.9716, 'lon': 77.5946}
            }
            return mock_coords.get(location, {'lat': 20.5937, 'lon': 78.9629})

        
        return {'location': location}

    except Exception as e:
        logger.warning(f"Geocoding failed for {location}: {e}")
     
        return {'lat': 20.5937, 'lon': 78.9629}

def get_weather_data(location):
    """Get current weather data for a location using WeatherAPI.com"""
    try:
        if WEATHER_API_KEY == 'demo_key':
            
            weather = MOCK_WEATHER_DATA.get(location, MOCK_WEATHER_DATA['Pune'])
            return {
                'location': location,
                'temperature': weather['temperature'],
                'humidity': weather['humidity'],
                'pressure': weather['pressure'],
                'wind_speed': weather['wind_speed'],
                'description': weather['description'],
                'icon': weather['icon'],
                'rainfall': weather['rainfall'],
                'uv_index': weather['uv_index'],
                'timestamp': datetime.now().isoformat(),
                'source': 'mock_data'
            }

       
        url = f"{WEATHER_BASE_URL}/current.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': location,
            'aqi': 'no'

        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            'location': location,
            'temperature': data['current']['temp_c'],
            'humidity': data['current']['humidity'],
            'pressure': data['current']['pressure_mb'],
            'wind_speed': data['current']['wind_kph'],
            'description': data['current']['condition']['text'],
            'icon': data['current']['condition']['icon'],
            'rainfall': data['current'].get('precip_mm', 0.0),
            'uv_index': data['current'].get('uv', 0.0),
            'timestamp': data['current']['last_updated'],
            'source': 'weatherapi'
        }

    except Exception as e:
        logger.error(f"Failed to get weather data for {location}: {e}")

        weather = MOCK_WEATHER_DATA.get(location, MOCK_WEATHER_DATA['Pune'])
        return {
            'location': location,
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'pressure': weather['pressure'],
            'wind_speed': weather['wind_speed'],
            'description': weather['description'],
            'icon': weather['icon'],
            'rainfall': weather['rainfall'],
            'uv_index': weather['uv_index'],
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_mock_data',
            'error': str(e)
        }

def get_weather_forecast(location, days=5):
    """Get weather forecast for a location using WeatherAPI.com"""
    try:
        if WEATHER_API_KEY == 'demo_key':
          
            base_temp = MOCK_WEATHER_DATA.get(location, MOCK_WEATHER_DATA['Pune'])['temperature']
            forecast = []

            for i in range(days):
                date = datetime.now() + timedelta(days=i)
                
                temp_variation = (i % 3 - 1) * 2  
                temp = base_temp + temp_variation

                forecast.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'temperature': round(temp, 1),
                    'humidity': 65 + (i % 5) * 3,
                    'description': ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Clear'][i % 5],
                    'rainfall': [0.0, 0.0, 0.0, 2.5, 0.0][i % 5],
                    'wind_speed': 10 + (i % 3) * 2
                })

            return {
                'location': location,
                'forecast': forecast,
                'source': 'mock_data'
            }

        url = f"{WEATHER_BASE_URL}/forecast.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': location,
            'days': min(days, 10), 
            'aqi': 'no',
            'alerts': 'no'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        forecast = []
        for day in data['forecast']['forecastday'][:days]:
            forecast.append({
                'date': day['date'],
                'temperature': day['day']['avgtemp_c'],
                'humidity': day['day']['avghumidity'],
                'description': day['day']['condition']['text'],
                'rainfall': day['day']['totalprecip_mm'],
                'wind_speed': day['day']['maxwind_kph']
            })

        return {
            'location': location,
            'forecast': forecast,
            'source': 'weatherapi'
        }

    except Exception as e:
        logger.error(f"Failed to get weather forecast for {location}: {e}")
        
        base_temp = MOCK_WEATHER_DATA.get(location, MOCK_WEATHER_DATA['Pune'])['temperature']
        forecast = []

        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            temp_variation = (i % 3 - 1) * 2
            temp = base_temp + temp_variation

            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'temperature': round(temp, 1),
                'humidity': 65 + (i % 5) * 3,
                'description': ['Sunny', 'Partly cloudy', 'Cloudy', 'Light rain', 'Clear'][i % 5],
                'rainfall': [0.0, 0.0, 0.0, 2.5, 0.0][i % 5],
                'wind_speed': 10 + (i % 3) * 2
            })

        return {
            'location': location,
            'forecast': forecast,
            'source': 'fallback_mock_data',
            'error': str(e)
        }

def get_agricultural_advice(location, current_crop=None):
    """Generate agricultural advice based on weather conditions"""
    try:
        weather_data = get_weather_data(location)

        advice = {
            'location': location,
            'current_weather': {
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'description': weather_data['description'],
                'rainfall': weather_data['rainfall']
            },
            'recommendations': [],
            'alerts': [],
            'optimal_conditions': {},
            'source': weather_data.get('source', 'unknown')
        }

       
        temp = weather_data['temperature']
        if temp < 10:
            advice['alerts'].append(" Cold weather alert: Protect crops from frost")
            advice['recommendations'].append("Use row covers or frost blankets to protect young plants")
        elif temp > 35:
            advice['alerts'].append(" Heat stress alert: High temperature may affect crop growth")
            advice['recommendations'].append("Increase irrigation frequency and provide shade for sensitive crops")
        elif 20 <= temp <= 30:
            advice['recommendations'].append("Optimal temperature range for most crops")

        
        humidity = weather_data['humidity']
        if humidity < 30:
            advice['recommendations'].append("Low humidity: Increase irrigation to prevent water stress")
        elif humidity > 80:
            advice['alerts'].append(" High humidity: Monitor for fungal diseases")
            advice['recommendations'].append("Ensure good air circulation and consider fungicide application")

        
        rainfall = weather_data['rainfall']
        if rainfall > 10:
            advice['alerts'].append(" Heavy rainfall expected: Prepare for waterlogging")
            advice['recommendations'].append("Improve drainage systems and avoid working in wet soil")
        elif rainfall < 1:
            advice['recommendations'].append(" Dry conditions: Schedule irrigation to maintain soil moisture")

        
        if current_crop:
            crop_advice = get_crop_specific_advice(current_crop.lower(), temp, humidity, rainfall)
            advice['recommendations'].extend(crop_advice)

       
        advice['recommendations'].extend([
            "Monitor soil moisture regularly",
            "Check crops for pest and disease symptoms",
            "Adjust fertilization based on crop growth stage"
        ])

        
        advice['optimal_conditions'] = {
            'temperature_range': '20-30C',
            'humidity_range': '40-70%',
            'general_advice': 'Maintain consistent soil moisture and monitor weather changes'
        }

        return advice

    except Exception as e:
        logger.error(f"Failed to generate agricultural advice for {location}: {e}")
        return {
            'location': location,
            'error': f"Unable to generate advice: {str(e)}",
            'recommendations': [
                "Monitor local weather conditions regularly",
                "Maintain proper irrigation schedules",
                "Check crops for signs of stress or disease"
            ],
            'source': 'error_fallback'
        }

def get_crop_specific_advice(crop, temperature, humidity, rainfall):
    """Get crop-specific agricultural advice"""
    advice = []

    crop_advice = {
        'wheat': {
            'temp_optimal': (15, 25),
            'humidity_optimal': (40, 60),
            'rainfall_sensitivity': 'moderate'
        },
        'rice': {
            'temp_optimal': (20, 35),
            'humidity_optimal': (60, 90),
            'rainfall_sensitivity': 'high'
        },
        'maize': {
            'temp_optimal': (20, 30),
            'humidity_optimal': (50, 80),
            'rainfall_sensitivity': 'moderate'
        },
        'cotton': {
            'temp_optimal': (25, 35),
            'humidity_optimal': (40, 70),
            'rainfall_sensitivity': 'low'
        },
        'groundnut': {
            'temp_optimal': (25, 35),
            'humidity_optimal': (50, 70),
            'rainfall_sensitivity': 'moderate'
        }
    }

    if crop in crop_advice:
        crop_info = crop_advice[crop]
        temp_min, temp_max = crop_info['temp_optimal']

        if temperature < temp_min:
            advice.append(f" Temperature too low for {crop} - consider protective measures")
        elif temperature > temp_max:
            advice.append(f" Temperature too high for {crop} - increase irrigation and provide shade")

        hum_min, hum_max = crop_info['humidity_optimal']
        if humidity < hum_min:
            advice.append(f" Humidity too low for {crop} - increase irrigation frequency")
        elif humidity > hum_max:
            advice.append(f" Humidity too high for {crop} - improve ventilation and monitor for diseases")

        if crop_info['rainfall_sensitivity'] == 'high' and rainfall > 5:
            advice.append(f" {crop} is sensitive to heavy rain - ensure proper drainage")
        elif crop_info['rainfall_sensitivity'] == 'low' and rainfall < 1:
            advice.append(f" {crop} needs consistent moisture - schedule irrigation")

    return advice


if __name__ == "__main__":
    
    print("Testing Weather Service...")

    
    weather = get_weather_data('Pune')
    print(f"Current weather in Pune: {weather}")

    forecast = get_weather_forecast('Pune', 3)
    print(f"3-day forecast for Pune: {forecast}")

   
    advice = get_agricultural_advice('Pune', 'wheat')
    print(f"Agricultural advice for Pune (wheat): {advice}")
