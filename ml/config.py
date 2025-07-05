import os
from decouple import config

# Database
DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:changeme@db:5432/smartcity')

# Model configuration
MODEL_PATH = config('MODEL_PATH', default='/app/models')

# Feature columns for prediction
FEATURE_COLUMNS = [
    'temperature', 'humidity', 'pressure', 'pm10', 'no2', 'so2', 'co', 'o3',
    'hour', 'day_of_week', 'month', 'is_weekend', 'season',
    'pm25_lag_1h', 'pm25_lag_3h', 'pm25_lag_6h', 'pm25_lag_12h', 'pm25_lag_24h',
    'temp_lag_1h', 'humidity_lag_1h',
    'pm25_rolling_mean_3h', 'pm25_rolling_mean_6h', 'pm25_rolling_mean_12h',
    'pm25_rolling_std_6h', 'pm25_rolling_max_6h', 'pm25_rolling_min_6h',
    'temp_rolling_mean_6h', 'humidity_rolling_mean_6h',
    'pm25_change_1h', 'pm25_change_3h',
    'temp_humidity_interaction', 'temp_pressure_interaction', 'wind_pollution_interaction',
    'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'traffic_level'
]

# Model hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 20,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'n_jobs': -1
}
