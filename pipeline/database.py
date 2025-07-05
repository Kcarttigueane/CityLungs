import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import pandas as pd
from config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        self.Session = sessionmaker(bind=self.engine)
        
    def insert_measurements(self, measurements):
        """Insert multiple measurements into the database"""
        if not measurements:
            logger.warning("No measurements to insert")
            return
            
        session = self.Session()
        try:
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(measurements)
            
            # Ensure all required columns exist
            required_columns = [
                'location_name', 'latitude', 'longitude', 'timestamp',
                'source'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Missing required column: {col}")
                    return
            
            # Insert using pandas to_sql for efficiency
            df.to_sql(
                'measurements',
                self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            session.commit()
            logger.info(f"Successfully inserted {len(measurements)} measurements")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting measurements: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_latest_measurement(self, location_name):
        """Get the latest measurement for a location"""
        session = self.Session()
        try:
            result = session.execute(
                text("""
                    SELECT * FROM measurements 
                    WHERE location_name = :location_name 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """),
                {"location_name": location_name}
            ).fetchone()
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching latest measurement: {str(e)}")
            return None
        finally:
            session.close()
    
    def check_alert_thresholds(self):
        """Check if any measurements exceed alert thresholds"""
        session = self.Session()
        try:
            # Get active alert configurations
            configs = session.execute(
                text("SELECT * FROM alert_configs WHERE is_enabled = true")
            ).fetchall()
            
            alerts = []
            
            for config in configs:
                # Validate parameter name to prevent SQL injection
                allowed_parameters = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'temperature', 'humidity']
                if config.parameter not in allowed_parameters:
                    logger.warning(f"Invalid parameter in alert config: {config.parameter}")
                    continue
                    
                # Check recent measurements against thresholds
                query = f"""
                    SELECT * FROM measurements 
                    WHERE {config.parameter} > :threshold 
                    AND timestamp > NOW() - INTERVAL '1 hour'
                    ORDER BY timestamp DESC
                """
                
                result = session.execute(
                    text(query),
                    {"threshold": config.threshold_value}
                ).fetchall()
                
                for measurement in result:
                    # Create alert if not already exists
                    existing = session.execute(
                        text("""
                            SELECT id FROM alerts 
                            WHERE location_name = :location 
                            AND alert_type = :type 
                            AND is_active = true
                            AND created_at > NOW() - INTERVAL '6 hours'
                        """),
                        {
                            "location": measurement.location_name,
                            "type": config.parameter
                        }
                    ).fetchone()
                    
                    if not existing:
                        # Safely get measurement value
                        actual_value = getattr(measurement, config.parameter, None)
                        if actual_value is not None:
                            alert = {
                                'alert_type': config.parameter,
                                'severity': config.severity,
                                'location_name': measurement.location_name,
                                'message': f"{config.parameter.upper()} exceeded threshold at {measurement.location_name}: {actual_value:.2f}",
                                'threshold_value': float(config.threshold_value),
                                'actual_value': float(actual_value),
                                'is_active': True,
                                'created_at': datetime.utcnow()
                            }
                            alerts.append(alert)
            
            if alerts:
                # Insert alerts
                pd.DataFrame(alerts).to_sql(
                    'alerts',
                    self.engine,
                    if_exists='append',
                    index=False
                )
                logger.info(f"Created {len(alerts)} new alerts")
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error checking alert thresholds: {str(e)}")
        finally:
            session.close()