#!/bin/bash

echo "🔍 Smart City Platform - Local Setup Verification"
echo "================================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC} ($(docker --version))"
else
    echo -e "${RED}✗ Not installed${NC}"
    exit 1
fi

# Check Docker Compose
echo -n "Checking Docker Compose... "
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC} ($(docker-compose --version))"
else
    echo -e "${RED}✗ Not installed${NC}"
    exit 1
fi

# Check .env file
echo -n "Checking .env file... "
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found${NC}"
    
    # Check for required variables
    required_vars=("DATABASE_URL" "DJANGO_SECRET_KEY" "OPENWEATHER_API_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            echo -e "  ${GREEN}✓${NC} $var is set"
        else
            echo -e "  ${RED}✗${NC} $var is missing"
        fi
    done
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Run: cp .env.example .env"
    exit 1
fi

echo ""
echo "🐳 Checking Docker containers..."
echo "--------------------------------"

# Start containers if not running
if [ "$1" == "--start" ]; then
    echo "Starting containers..."
    docker-compose up -d
    sleep 10
fi

# Check each service
services=("db" "backend" "frontend" "ml_service" "pipeline")
all_running=true

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "citylungs-$service.*Up"; then
        echo -e "${GREEN}✓${NC} $service is running"
    else
        echo -e "${RED}✗${NC} $service is not running"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    echo ""
    echo -e "${YELLOW}Some services are not running. Run: docker-compose up -d${NC}"
    exit 1
fi

echo ""
echo "🔌 Testing service endpoints..."
echo "-------------------------------"

# Test Database
echo -n "Testing Database connection... "
if docker-compose exec -T db psql -U postgres -d smartcity -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Connection failed${NC}"
fi

# Test Backend
echo -n "Testing Backend API... "
if curl -s -f http://localhost:8000/api/ > /dev/null; then
    echo -e "${GREEN}✓ Responding${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Test Frontend
echo -n "Testing Frontend... "
if curl -s -f http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Responding${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

# Test ML Service
echo -n "Testing ML Service... "
if curl -s -f http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✓ Responding${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
fi

echo ""
echo "📊 Checking data..."
echo "------------------"

# Check if we have measurements
measurement_count=$(docker-compose exec -T backend python -c "
from api.models import Measurement
print(Measurement.objects.count())
" 2>/dev/null | tr -d '\r\n')

if [ -n "$measurement_count" ] && [ "$measurement_count" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $measurement_count measurements"
else
    echo -e "${YELLOW}⚠${NC} No measurements found"
    echo "  To generate sample data, run:"
    echo "  ./generate_sample_data.sh"
fi

# Check if we have users
user_count=$(docker-compose exec -T backend python -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.count())
" 2>/dev/null | tr -d '\r\n')

if [ -n "$user_count" ] && [ "$user_count" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $user_count users"
else
    echo -e "${YELLOW}⚠${NC} No users found"
    echo "  To create admin user, run:"
    echo "  docker-compose exec backend python manage.py createsuperuser"
fi

echo ""
echo "🎉 Setup verification complete!"
echo ""
echo "📱 Access your application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/api"
echo "   Admin:    http://localhost:8000/admin"
echo ""
echo "📝 Quick commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop all:     docker-compose down"
echo "   Restart all:  docker-compose restart"
echo ""

# generate_sample_data.sh - Script to generate sample data
cat > generate_sample_data.sh << 'SCRIPT'
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
SCRIPT

chmod +x generate_sample_data.sh

echo "💡 Tip: To generate sample data, run: ./generate_sample_data.sh"