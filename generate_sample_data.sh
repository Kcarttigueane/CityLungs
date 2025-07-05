#!/bin/bash

echo "🌱 Generating sample data..."

docker-compose exec backend python manage.py shell << 'EOF'
from api.models import Measurement, AlertConfig
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random

User = get_user_model()

# Create test user if not exists
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        role='user'
    )
    print("✓ Created test user (username: testuser, password: testpass123)")

# Generate measurements
locations = [
    {"name": "Paris City Center", "lat": 48.8566, "lon": 2.3522},
    {"name": "Paris Nord", "lat": 48.8809, "lon": 2.3553},
    {"name": "Paris Est", "lat": 48.8619, "lon": 2.3956}
]

base_time = datetime.now()
count = 0

for location in locations:
    for i in range(72):  # 3 days of hourly data
        timestamp = base_time - timedelta(hours=i)
        
        # Simulate daily patterns
        hour = timestamp.hour
        traffic_base = 5
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            traffic_base = 8
        elif 22 <= hour or hour <= 6:  # Night
            traffic_base = 2
        
        Measurement.objects.create(
            location_name=location["name"],
            latitude=location["lat"],
            longitude=location["lon"],
            timestamp=timestamp,
            temperature=15 + 10 * random.random(),
            humidity=40 + 40 * random.random(),
            pressure=1000 + 30 * random.random(),
            pm25=20 + 30 * random.random() + (traffic_base * 2),
            pm10=30 + 40 * random.random() + (traffic_base * 3),
            no2=15 + 25 * random.random(),
            so2=5 + 15 * random.random(),
            co=0.3 + 0.7 * random.random(),
            o3=30 + 40 * random.random(),
            aqi=int(50 + 50 * random.random() + (traffic_base * 5)),
            traffic_level=traffic_base + random.randint(-2, 2),
            source='sample_data'
        )
        count += 1

print(f"✓ Created {count} sample measurements")

# Create alert configs if not exist
if AlertConfig.objects.count() == 0:
    configs = [
        {'parameter': 'pm25', 'threshold_value': 35.0, 'severity': 'medium'},
        {'parameter': 'pm25', 'threshold_value': 55.0, 'severity': 'high'},
        {'parameter': 'pm25', 'threshold_value': 150.0, 'severity': 'critical'},
        {'parameter': 'aqi', 'threshold_value': 100, 'severity': 'medium'},
        {'parameter': 'aqi', 'threshold_value': 150, 'severity': 'high'},
    ]
    
    for config in configs:
        AlertConfig.objects.create(**config, is_enabled=True)
    
    print(f"✓ Created {len(configs)} alert configurations")

print("\n✅ Sample data generation complete!")
print("\n📊 Summary:")
print(f"   - Users: {User.objects.count()}")
print(f"   - Measurements: {Measurement.objects.count()}")
print(f"   - Alert Configs: {AlertConfig.objects.count()}")
EOF

echo ""
echo "🎯 Next steps:"
echo "1. Open http://localhost:3000"
echo "2. Login with: testuser / testpass123"
echo "3. View the dashboard with sample data"
