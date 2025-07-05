import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
    
    def get_training_data(self, location=None, days=90):
        """Fetch historical data for training"""
        base_query = """
            SELECT 
                location_name, timestamp, temperature, humidity, pressure,
                pm25, pm10, no2, so2, co, o3, traffic_level
            FROM measurements
            WHERE timestamp >= NOW() - INTERVAL %(days)s
        """
        
        params = {'days': f'{days} days'}
        
        if location and location != 'all':
            base_query += " AND location_name = %(location)s"
            params['location'] = location
        
        query = base_query + " ORDER BY location_name, timestamp"
        
        try:
            # Use direct string substitution for PostgreSQL
            if location and location != 'all':
                final_query = f"""
                    SELECT 
                        location_name, timestamp, temperature, humidity, pressure,
                        pm25, pm10, no2, so2, co, o3, traffic_level
                    FROM measurements
                    WHERE timestamp >= NOW() - INTERVAL '{days} days'
                    AND location_name = '{location}'
                    ORDER BY location_name, timestamp
                """
            else:
                final_query = f"""
                    SELECT 
                        location_name, timestamp, temperature, humidity, pressure,
                        pm25, pm10, no2, so2, co, o3, traffic_level
                    FROM measurements
                    WHERE timestamp >= NOW() - INTERVAL '{days} days'
                    ORDER BY location_name, timestamp
                """
            
            df = pd.read_sql(final_query, self.engine)
            logger.info(f"Fetched {len(df)} records for training")
            return df
        except Exception as e:
            logger.error(f"Error fetching training data: {str(e)}")
            return pd.DataFrame()
    
    def get_latest_features(self, location, hours=24):
        """Get latest features for prediction"""
        query = """
            SELECT * FROM measurements
            WHERE location_name = %(location)s
            AND timestamp >= NOW() - INTERVAL %(hours)s
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        """
        
        try:
            # Use direct string substitution
            final_query = f"""
                SELECT * FROM measurements
                WHERE location_name = '{location}'
                AND timestamp >= NOW() - INTERVAL '{hours} hours'
                ORDER BY timestamp DESC
                LIMIT {hours}
            """
            
            df = pd.read_sql(final_query, self.engine)
            return df.sort_values('timestamp')  # Sort ascending for feature engineering
        except Exception as e:
            logger.error(f"Error fetching latest features: {str(e)}")
            return pd.DataFrame()
    
    def save_predictions(self, predictions):
        """Save predictions to database"""
        try:
            predictions.to_sql(
                'predictions',
                self.engine,
                if_exists='append',
                index=False
            )
            logger.info(f"Saved {len(predictions)} predictions")
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")