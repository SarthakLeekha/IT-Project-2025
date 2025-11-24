import logging
from datetime import datetime

logger = logging.getLogger(__name__)



def get_coordinates(location):
    """Return default coordinates for offline operation"""
    return {'lat': 20.5937, 'lon': 78.9629}

def get_weather_data(location):
    """Return offline weather data message"""
    return {
        'location': location,
        'temperature': 25.0,
        'humidity': 60,
        'pressure': 1013,
        'wind_speed': 10.0,
        'description': 'Weather data unavailable (offline mode)',
        'icon': '01d',
        'rainfall': 0.0,
        'uv_index': 5.0,
        'timestamp': datetime.now().isoformat(),
        'source': 'offline_mode',
        'message': 'Weather features are disabled in offline mode'
    }

def get_weather_forecast(location, days=5):
    """Return offline forecast message"""
    forecast = []
    for i in range(days):
        forecast.append({
            'date': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).strftime('%Y-%m-%d'),
            'temperature': 25.0,
            'humidity': 60,
            'description': 'Forecast unavailable (offline mode)',
            'rainfall': 0.0,
            'wind_speed': 10.0
        })

    return {
        'location': location,
        'forecast': forecast,
        'source': 'offline_mode',
        'message': 'Weather forecast is disabled in offline mode'
    }

def get_agricultural_advice(location, current_crop=None):
    """Return offline agricultural advice"""
    advice = {
        'location': location,
        'current_weather': {
            'temperature': 25.0,
            'humidity': 60,
            'description': 'Weather data unavailable',
            'rainfall': 0.0
        },
        'recommendations': [
            "Weather-based advice unavailable in offline mode",
            "Monitor local weather conditions manually",
            "Use general agricultural best practices",
            "Check soil moisture regularly",
            "Observe crop health and adjust practices accordingly"
        ],
        'alerts': [],
        'optimal_conditions': {
            'temperature_range': '20-30°C',
            'humidity_range': '40-70%',
            'general_advice': 'Weather monitoring disabled in offline mode'
        },
        'source': 'offline_mode',
        'message': 'Agricultural weather advice is disabled in offline mode'
    }

    if current_crop:
        advice['recommendations'].insert(0, f"For {current_crop}: Use standard cultivation practices")

    return advice

def get_crop_specific_advice(crop, temperature, humidity, rainfall):
    """Return offline crop advice"""
    return [f"Crop-specific weather advice for {crop} is unavailable in offline mode"]
