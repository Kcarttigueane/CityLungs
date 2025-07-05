import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self):
        pass
    
    def transform(self, weather_data, air_quality_data):
        """Combine and transform data from multiple sources"""
        # Create a mapping by location
        weather_map = {w['location_name']: w for w in weather_data}
        air_quality_map = {a['location_name']: a for a in air_quality_data}
        
        combined_data = []
        
        # Merge data by location
        all_locations = set(weather_map.keys()) | set(air_quality_map.keys())
        
        for location in all_locations:
            measurement = {
                'location_name': location,
                'timestamp': datetime.utcnow()
            }
            
            # Add weather data
            if location in weather_map:
                weather = weather_map[location]
                measurement.update({
                    'latitude': weather['latitude'],
                    'longitude': weather['longitude'],
                    'temperature': weather.get('temperature'),
                    'humidity': weather.get('humidity'),
                    'pressure': weather.get('pressure')
                })
            
            # Add air quality data
            if location in air_quality_map:
                air_quality = air_quality_map[location]
                measurement.update({
                    'pm25': air_quality.get('pm25'),
                    'pm10': air_quality.get('pm10'),
                    'no2': air_quality.get('no2'),
                    'so2': air_quality.get('so2'),
                    'co': air_quality.get('co'),
                    'o3': air_quality.get('o3'),
                    'aqi': air_quality.get('aqi')
                })
                
                # Use air quality coordinates if weather data missing
                if 'latitude' not in measurement:
                    measurement['latitude'] = air_quality['latitude']
                    measurement['longitude'] = air_quality['longitude']
            
            # Add synthetic traffic data (for demo purposes)
            measurement['traffic_level'] = self.estimate_traffic_level(measurement['timestamp'])
            
            # Determine source
            if location in weather_map and location in air_quality_map:
                measurement['source'] = 'combined'
            elif location in weather_map:
                measurement['source'] = 'openweather'
            else:
                measurement['source'] = 'openaq'
            
            # Ensure we have coordinates
            if 'latitude' in measurement and 'longitude' in measurement:
                combined_data.append(measurement)
            else:
                logger.warning(f"Skipping measurement for {location} - missing coordinates")
        
        return combined_data
    
    def estimate_traffic_level(self, timestamp):
        """Estimate traffic level based on time of day (synthetic data)"""
        hour = timestamp.hour
        
        # Morning rush hour (7-9 AM)
        if 7 <= hour <= 9:
            return random.randint(7, 10)
        # Evening rush hour (5-7 PM)
        elif 17 <= hour <= 19:
            return random.randint(7, 10)
        # Daytime
        elif 9 < hour < 17:
            return random.randint(4, 7)
        # Night time
        else:
            return random.randint(1, 3)