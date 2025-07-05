#!/usr/bin/env python3
"""
Generate sample data for ML training and testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
import os

# Add backend path to import Django models
sys.path.append('./backend')
os.environ.setdefault('DJANGO_SECRET_KEY', 'sample-data-generation-key')

from sqlalchemy import create_engine
from decouple import config

# Database connection - use localhost when running outside Docker
DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:localpassword123@localhost:5432/smartcity')

def generate_sample_measurements(days=30, locations=None):
    """Generate sample air quality measurements"""
    
    if locations is None:
        locations = [
            {'name': 'Paris City Center', 'lat': 48.8566, 'lon': 2.3522},
            {'name': 'Paris Nord', 'lat': 48.8809, 'lon': 2.3553},
            {'name': 'Paris Est', 'lat': 48.8619, 'lon': 2.3956}
        ]
    
    measurements = []
    
    # Generate data for each location
    for location in locations:
        print(f"Generating data for {location['name']}...")
        
        # Generate hourly data for the specified period
        start_time = datetime.now() - timedelta(days=days)
        
        for hour in range(days * 24):
            timestamp = start_time + timedelta(hours=hour)
            
            # Simulate daily and seasonal patterns
            hour_of_day = timestamp.hour
            day_of_year = timestamp.timetuple().tm_yday
            
            # Base pollution levels with daily patterns
            base_pm25 = 20 + 15 * np.sin(2 * np.pi * hour_of_day / 24 - np.pi/2)  # Peak in evening
            base_pm25 += 10 * np.sin(2 * np.pi * day_of_year / 365)  # Seasonal variation
            
            # Add rush hour effects
            if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                base_pm25 += random.uniform(5, 15)
            
            # Weather patterns
            temp_base = 15 + 10 * np.sin(2 * np.pi * day_of_year / 365)  # Seasonal temperature
            temp_daily = 5 * np.sin(2 * np.pi * hour_of_day / 24 - np.pi/4)  # Daily temperature
            temperature = temp_base + temp_daily + random.uniform(-3, 3)
            
            humidity = 60 + 20 * np.sin(2 * np.pi * day_of_year / 365 + np.pi) + random.uniform(-10, 10)
            humidity = max(20, min(90, humidity))
            
            pressure = 1013 + random.uniform(-20, 20)
            
            # Correlate pollution with weather
            if humidity > 70:  # High humidity increases pollution
                base_pm25 *= 1.2
            if temperature < 5:  # Cold weather increases pollution (heating)
                base_pm25 *= 1.3
                
            # Add noise
            pm25 = max(5, base_pm25 + random.uniform(-5, 5))
            pm10 = pm25 * random.uniform(1.5, 2.0)
            
            # Other pollutants correlated with PM2.5
            no2 = pm25 * random.uniform(1.2, 2.0) + random.uniform(-5, 5)
            so2 = pm25 * random.uniform(0.3, 0.8) + random.uniform(-2, 2)
            co = pm25 * random.uniform(0.5, 1.5) + random.uniform(-3, 3)
            o3 = max(0, 80 - pm25 * 0.5 + random.uniform(-10, 10))  # Ozone inversely correlated
            
            # Traffic level based on time of day
            if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                traffic_level = random.randint(7, 10)
            elif 9 < hour_of_day < 17:
                traffic_level = random.randint(4, 7)
            else:
                traffic_level = random.randint(1, 3)
            
            measurement = {
                'location_name': location['name'],
                'latitude': location['lat'],
                'longitude': location['lon'],
                'timestamp': timestamp,
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'pressure': round(pressure, 2),
                'pm25': round(pm25, 2),
                'pm10': round(pm10, 2),
                'no2': round(max(0, no2), 2),
                'so2': round(max(0, so2), 2),
                'co': round(max(0, co), 2),
                'o3': round(max(0, o3), 2),
                'traffic_level': traffic_level,
                'source': 'generated',
                'created_at': datetime.now()
            }
            
            measurements.append(measurement)
    
    return measurements

def insert_sample_data(measurements):
    """Insert sample data into database"""
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.DataFrame(measurements)
        
        print(f"Inserting {len(measurements)} measurements into database...")
        df.to_sql('measurements', engine, if_exists='append', index=False, method='multi')
        print("✓ Sample data inserted successfully")
        
        # Print statistics
        print(f"\nData statistics:")
        print(f"Total measurements: {len(measurements)}")
        print(f"Locations: {df['location_name'].nunique()}")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"Average PM2.5: {df['pm25'].mean():.2f} μg/m³")
        
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        return False
    
    return True

def main():
    """Main function"""
    print("CityLungs Sample Data Generator")
    print("=" * 40)
    
    # Generate sample data
    days = 30  # Generate 30 days of data
    measurements = generate_sample_measurements(days=days)
    
    # Insert into database
    success = insert_sample_data(measurements)
    
    if success:
        print(f"\n🎉 Successfully generated {days} days of sample data!")
        print("You can now test ML training and predictions.")
    else:
        print("\n❌ Failed to generate sample data.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)