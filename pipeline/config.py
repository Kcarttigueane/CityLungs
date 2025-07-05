import os
from decouple import config

# Database
DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:changeme@db:5432/smartcity')

# API Keys
OPENWEATHER_API_KEY = config('OPENWEATHER_API_KEY')
OPENAQ_API_KEY = config('OPENAQ_API_KEY', default='')

# Locations to monitor
MONITORED_LOCATIONS = [
    {
        'name': 'Paris City Center',
        'lat': 48.8566,
        'lon': 2.3522,
        'openaq_location_id': 'FR001'
    },
    {
        'name': 'Paris Nord',
        'lat': 48.8809,
        'lon': 2.3553,
        'openaq_location_id': 'FR002'
    },
    {
        'name': 'Paris Est',
        'lat': 48.8619,
        'lon': 2.3956,
        'openaq_location_id': 'FR003'
    }
]

# Collection intervals (in minutes)
WEATHER_COLLECTION_INTERVAL = 30
AIR_QUALITY_COLLECTION_INTERVAL = 30