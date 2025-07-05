import requests
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENWEATHER_API_KEY, MONITORED_LOCATIONS

logger = logging.getLogger(__name__)

class OpenWeatherCollector:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def collect(self):
        """Collect weather data for all monitored locations"""
        measurements = []
        
        for location in MONITORED_LOCATIONS:
            try:
                data = self.fetch_weather_data(location)
                if data:
                    measurement = self.transform_weather_data(data, location)
                    measurements.append(measurement)
            except Exception as e:
                logger.error(f"Error collecting weather data for {location['name']}: {str(e)}")
        
        return measurements
    
    def fetch_weather_data(self, location):
        """Fetch weather data from OpenWeatherMap API"""
        if not self.api_key:
            logger.error("OpenWeather API key not configured")
            return None
            
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': self.api_key,
            'units': 'metric'
        }
        
        headers = {'User-Agent': 'CityLungs/1.0'}
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {location['name']}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {str(e)}")
            return None
    
    def transform_weather_data(self, data, location):
        """Transform API response to measurement format"""
        measurement = {
            'location_name': location['name'],
            'latitude': location['lat'],
            'longitude': location['lon'],
            'timestamp': datetime.utcnow(),
            'source': 'openweather'
        }
        
        # Extract weather data safely
        main_data = data.get('main', {})
        wind_data = data.get('wind', {})
        
        measurement['temperature'] = main_data.get('temp')
        measurement['humidity'] = main_data.get('humidity')
        measurement['pressure'] = main_data.get('pressure')
        measurement['wind_speed'] = wind_data.get('speed', 0)
        measurement['wind_deg'] = wind_data.get('deg', 0)
        
        # Add visibility if available
        if 'visibility' in data:
            measurement['visibility'] = data['visibility']
        
        return measurement