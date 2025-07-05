import pandas as pd
import numpy as np
from datetime import datetime

class FeatureEngineer:
    def __init__(self):
        pass
    
    def create_features(self, df):
        """Create features for ML models"""
        df = df.copy()
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by location and timestamp
        df = df.sort_values(['location_name', 'timestamp'])
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Group by location for lag features
        grouped = df.groupby('location_name')
        
        # Lag features
        df['pm25_lag_1h'] = grouped['pm25'].shift(1)
        df['pm25_lag_3h'] = grouped['pm25'].shift(3)
        df['pm25_lag_6h'] = grouped['pm25'].shift(6)
        df['pm25_lag_12h'] = grouped['pm25'].shift(12)
        df['pm25_lag_24h'] = grouped['pm25'].shift(24)
        
        df['temp_lag_1h'] = grouped['temperature'].shift(1)
        df['humidity_lag_1h'] = grouped['humidity'].shift(1)
        
        # Rolling statistics
        df['pm25_rolling_mean_3h'] = grouped['pm25'].rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)
        df['pm25_rolling_mean_6h'] = grouped['pm25'].rolling(window=6, min_periods=1).mean().reset_index(0, drop=True)
        df['pm25_rolling_mean_12h'] = grouped['pm25'].rolling(window=12, min_periods=1).mean().reset_index(0, drop=True)
        df['pm25_rolling_std_6h'] = grouped['pm25'].rolling(window=6, min_periods=1).std().reset_index(0, drop=True)
        
        # Additional rolling features
        df['pm25_rolling_max_6h'] = grouped['pm25'].rolling(window=6, min_periods=1).max().reset_index(0, drop=True)
        df['pm25_rolling_min_6h'] = grouped['pm25'].rolling(window=6, min_periods=1).min().reset_index(0, drop=True)
        df['temp_rolling_mean_6h'] = grouped['temperature'].rolling(window=6, min_periods=1).mean().reset_index(0, drop=True)
        df['humidity_rolling_mean_6h'] = grouped['humidity'].rolling(window=6, min_periods=1).mean().reset_index(0, drop=True)
        
        # Weather interaction features
        df['temp_humidity_interaction'] = df['temperature'] * df['humidity'] / 100
        df['temp_pressure_interaction'] = df['temperature'] * df['pressure'] / 1000
        df['wind_pollution_interaction'] = df.get('wind_speed', 0) * df.get('pm25', 0)
        
        # PM2.5 change rate
        df['pm25_change_1h'] = df['pm25'] - df['pm25_lag_1h']
        df['pm25_change_3h'] = df['pm25'] - df['pm25_lag_3h']
        
        # Season encoding
        df['season'] = df['month'].apply(self._get_season)
        
        # Hour buckets
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Day of year cyclical encoding
        df['day_of_year'] = df['timestamp'].dt.dayofyear
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        return df
    
    def _get_season(self, month):
        """Get season from month"""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Fall
    
    def prepare_for_prediction(self, df, feature_columns):
        """Prepare features for prediction"""
        # Fill missing values using newer pandas methods
        df = df.ffill().bfill()
        
        # Ensure all required columns exist
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Handle infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        return df[feature_columns]