# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CityLungs is a multi-service smart city air quality monitoring platform with the following architecture:

- **Frontend**: Vue.js 3 application with Tailwind CSS, Vite, and Leaflet maps
- **Backend**: Django REST API with PostgreSQL database
- **ML Service**: Flask-based machine learning service for air quality predictions
- **Data Pipeline**: Python service for collecting data from OpenAQ and OpenWeather APIs
- **Database**: PostgreSQL with indexed tables for measurements, predictions, and alerts

## Development Commands

### Local Development (Docker)
```bash
# Start all services
docker-compose up -d

# Start with automatic system verification and data generation
./start_complete_system.sh

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Verify setup and health check all services
./verify-setup.sh

# Generate sample data
./generate_sample_data.sh
```

### Frontend Development
```bash
cd frontend
npm run dev          # Development server (port 3000)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # ESLint with auto-fix
npm run test:unit    # Run Vitest unit tests
```

### Backend Development
```bash
cd backend
python manage.py runserver     # Development server (port 8000)
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### ML Service Development
```bash
cd ml
python app.py        # Start Flask service (port 5000 in container, 5001 on host)
python run_standalone.py  # Run standalone outside Docker
```

### Pipeline Development
```bash
cd pipeline
python scheduler.py  # Run ETL pipeline with scheduling
python run_standalone.py  # Run single collection cycle
```

## Core Architecture

### Data Models (backend/api/models.py)
- **User**: Extended AbstractUser with role-based access (user/admin)
- **Measurement**: Air quality metrics with location, timestamp, and environmental data
  - Custom table name: `measurements`
  - Indexed on location_name + timestamp for performance
  - Supports PM2.5, PM10, NO2, SO2, CO, O3, AQI, traffic levels
- **Prediction**: ML-generated PM2.5 predictions with confidence scores
  - Custom table name: `predictions`
  - Links prediction timestamp to target timestamp
- **Alert**: Configurable alerts based on threshold violations
  - Custom table name: `alerts`
  - Supports severity levels (low, medium, high, critical)
- **AlertConfig**: Admin-configurable alert parameters
  - Custom table name: `alert_configs`

### Frontend Structure (frontend/src/)
- **Views**: Dashboard, Alerts, Predictions, Admin, Login/Register
- **Components**: EnvironmentMap (Leaflet), MetricCard, NotificationToast, StatusIndicator
- **Stores**: Pinia stores for auth, measurements, predictions, alerts, and API state
- **Services**: Axios-based API client with authentication handling
- **Router**: Vue Router with authentication guards

### ML Pipeline (ml/)
- **app.py**: Flask API with endpoints for predictions, training, and health checks
- **prediction_service.py**: Generates PM2.5 forecasts using trained models
- **model_trainer.py**: Trains and evaluates ML models on historical data
- **feature_engineering.py**: Processes environmental and temporal features
- **models/**: Stored trained models (Random Forest, XGBoost) with metrics

### Data Collection Pipeline (pipeline/)
- **scheduler.py**: ETL pipeline with scheduled data collection
- **collectors/openaq.py**: Fetches real-time air quality data from OpenAQ API
- **collectors/openweather.py**: Retrieves weather data for correlations
- **transformers/data_transformer.py**: Normalizes and validates incoming data
- **database.py**: Database operations and alert threshold checking

## Key Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_SECRET_KEY`: Django secret key
- `OPENWEATHER_API_KEY`: OpenWeather API key (currently: 486af2d663884acd198647a31cf757e9)
- `VITE_API_URL`: Frontend API endpoint (development: http://localhost:8000/api)

### Service Ports
- Frontend: 3000
- Backend: 8000
- ML Service: 5001 (mapped from container port 5000)
- Database: 5432

### Database Schema
Tables use custom names (`users`, `measurements`, `predictions`, `alerts`, `alert_configs`) with optimized indexes for location/timestamp queries.

## Development Patterns

### API Endpoints
- Authentication: JWT-based with role permissions
- Measurements: CRUD operations with filtering and pagination
- Predictions: ML service integration for forecasting
- Alerts: Real-time threshold monitoring

### Frontend State Management
- Pinia stores handle authentication, data fetching, and UI state
- Vue Router manages navigation and route guards
- Composables pattern for reusable logic

### ML Service API
- `/health`: Health check endpoint
- `/predict`: Generate PM2.5 predictions for location
- `/train`: Trigger model training (supports specific locations)
- `/models`: List available trained models
- `/metrics/<model_name>`: Get performance metrics for specific model

### Testing Strategy
- Frontend: Vitest for unit tests
- Backend: Django test framework
- ML Service: Custom validation scripts
- System tests: test_pipeline.py, test_pipeline_simple.py

## Production Deployment

The application is configured for Railway deployment with:
- Multi-service docker-compose setup
- Whitenoise for static file serving
- Environment-based configuration
- Separate production docker-compose.prod.yml
- Nginx reverse proxy configuration

## Common Tasks

### Adding New Environmental Parameters
1. Update `Measurement` model in backend/api/models.py
2. Create and run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Update serializers and views in backend/api/
4. Add frontend components and charts
5. Update ML feature engineering in ml/feature_engineering.py

### Configuring New Alert Types
1. Create AlertConfig entries via admin or API
2. Update alert processing logic in pipeline/database.py
3. Add frontend notification handling in stores/alerts.js

### Training New ML Models
1. Ensure sufficient historical data in database
2. POST to `/train` endpoint on ML service (localhost:5001)
3. Monitor training metrics and validation scores
4. Models are automatically saved to ml/models/ directory

### System Initialization
1. Run `./start_complete_system.sh` for complete setup
2. Use `./verify-setup.sh --start` to start and verify all services
3. Generate sample data with `./generate_sample_data.sh`
4. Default test user: username `testuser`, password `testpass123`