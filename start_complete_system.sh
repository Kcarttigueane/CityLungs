#!/bin/bash

# CityLungs Complete System Startup Script

echo "🏭 Starting CityLungs Smart City Platform"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start the complete system
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker services are running"
else
    echo "❌ Some services failed to start"
    docker-compose logs
    exit 1
fi

# Generate sample data if database is empty
echo "📊 Checking for existing data..."
python3 -c "
import sys
sys.path.append('./backend')
import os
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-key')
from sqlalchemy import create_engine, text
try:
    engine = create_engine('postgresql://postgres:localpassword123@localhost:5432/smartcity')
    result = engine.execute(text('SELECT COUNT(*) FROM measurements')).scalar()
    if result == 0:
        print('NO_DATA')
    else:
        print(f'FOUND_{result}_RECORDS')
except:
    print('NO_DATA')
" > /tmp/data_check.txt

if grep -q "NO_DATA" /tmp/data_check.txt; then
    echo "📈 No data found. Generating sample data..."
    python3 generate_sample_ml_data.py
    if [ $? -eq 0 ]; then
        echo "✅ Sample data generated successfully"
    else
        echo "⚠️  Warning: Failed to generate sample data"
    fi
else
    RECORD_COUNT=$(cat /tmp/data_check.txt | grep -o '[0-9]\+')
    echo "✅ Found existing data: $RECORD_COUNT records"
fi

# Clean up
rm -f /tmp/data_check.txt

echo ""
echo "🎉 CityLungs system is starting up!"
echo ""
echo "📱 Services:"
echo "   • Frontend:    http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • ML Service:  http://localhost:5001"
echo "   • Database:    localhost:5432"
echo ""
echo "🧪 Testing:"
echo "   python3 test_pipeline.py"
echo ""
echo "📊 Monitoring:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"

# Optionally run tests
if [ "$1" = "--test" ]; then
    echo ""
    echo "🧪 Running system tests..."
    sleep 15  # Give services more time to start
    python3 test_pipeline.py
fi