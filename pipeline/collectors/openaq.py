import requests
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAQ_API_KEY, MONITORED_LOCATIONS

logger = logging.getLogger(__name__)

class OpenAQCollector:
    def __init__(self):
        self.api_key = OPENAQ_API_KEY
        self.base_url = "https://api.openaq.org/v2/latest"
        
    def collect(self):
        """Collect air quality data for all monitored locations"""
        measurements = []
        
        for location in MONITORED_LOCATIONS:
            try:
                data = self.fetch_air_quality_data(location)
                if data:
                    measurement = self.transform_air_quality_data(data, location)
                    measurements.append(measurement)
            except Exception as e:
                logger.error(f"Error collecting air quality data for {location['name']}: {str(e)}")
        
        return measurements
    
    def fetch_air_quality_data(self, location):
        """Fetch air quality data from OpenAQ API"""
        params = {
            'coordinates': f"{location['lat']},{location['lon']}",
            'radius': 5000,  # 5km radius
            'limit': 1,
            'order_by': 'lastUpdated',
            'sort': 'desc'
        }
        
        headers = {'User-Agent': 'CityLungs/1.0'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                return data['results'][0]
            else:
                logger.warning(f"No air quality data found for {location['name']}")
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {location['name']}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching air quality data: {str(e)}")
            return None
    
    def transform_air_quality_data(self, data, location):
        """Transform API response to measurement format"""
        measurement = {
            'location_name': location['name'],
            'latitude': location['lat'],
            'longitude': location['lon'],
            'timestamp': datetime.utcnow(),
            'source': 'openaq'
        }
        
        # Extract measurements by parameter
        measurements_data = data.get('measurements', [])
        if not measurements_data:
            logger.warning(f"No measurements in data for {location['name']}")
            return measurement
        
        for m in measurements_data:
            parameter = m.get('parameter')
            value = m.get('value')
            
            if value is not None and isinstance(value, (int, float)):
                if parameter == 'pm25':
                    measurement['pm25'] = float(value)
                elif parameter == 'pm10':
                    measurement['pm10'] = float(value)
                elif parameter == 'no2':
                    measurement['no2'] = float(value)
                elif parameter == 'so2':
                    measurement['so2'] = float(value)
                elif parameter == 'co':
                    measurement['co'] = float(value)
                elif parameter == 'o3':
                    measurement['o3'] = float(value)
        
        # Calculate AQI if PM2.5 is available
        if measurement.get('pm25'):
            measurement['aqi'] = self.calculate_aqi(measurement['pm25'])
        
        return measurement
    
    def calculate_aqi(self, pm25):
        """Calculate AQI from PM2.5 concentration"""
        # US EPA AQI calculation for PM2.5
        if pm25 <= 12.0:
            return int((50 - 0) / (12.0 - 0) * (pm25 - 0) + 0)
        elif pm25 <= 35.4:
            return int((100 - 51) / (35.4 - 12.1) * (pm25 - 12.1) + 51)
        elif pm25 <= 55.4:
            return int((150 - 101) / (55.4 - 35.5) * (pm25 - 35.5) + 101)
        elif pm25 <= 150.4:
            return int((200 - 151) / (150.4 - 55.5) * (pm25 - 55.5) + 151)
        elif pm25 <= 250.4:
            return int((300 - 201) / (250.4 - 150.5) * (pm25 - 150.5) + 201)
        else:
            return int((500 - 301) / (500.4 - 250.5) * (pm25 - 250.5) + 301)