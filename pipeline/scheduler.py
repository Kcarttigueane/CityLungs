import schedule
import time
import logging
from collectors.openweather import OpenWeatherCollector
from collectors.openaq import OpenAQCollector
from transformers.data_transformer import DataTransformer
from database import DatabaseManager
from config import WEATHER_COLLECTION_INTERVAL, AIR_QUALITY_COLLECTION_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.transformer = DataTransformer()
        self.weather_collector = OpenWeatherCollector()
        self.air_quality_collector = OpenAQCollector()
        
    def run_pipeline(self):
        """Main ETL pipeline execution"""
        try:
            logger.info("Starting ETL pipeline run...")
            
            # Collect data from sources
            logger.info("Collecting weather data...")
            weather_data = self.weather_collector.collect()
            logger.info(f"Collected {len(weather_data)} weather measurements")
            
            logger.info("Collecting air quality data...")
            air_quality_data = self.air_quality_collector.collect()
            logger.info(f"Collected {len(air_quality_data)} air quality measurements")
            
            # Transform data
            logger.info("Transforming data...")
            transformed_data = self.transformer.transform(weather_data, air_quality_data)
            logger.info(f"Transformed {len(transformed_data)} total measurements")
            
            # Load to database
            if transformed_data:
                logger.info("Loading data to database...")
                self.db.insert_measurements(transformed_data)
                
                # Check for alerts
                logger.info("Checking alert thresholds...")
                self.db.check_alert_thresholds()
            else:
                logger.warning("No data to load")
            
            logger.info("Pipeline run completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)

def main():
    """Main scheduler function"""
    logger.info("Initializing Smart City ETL Pipeline...")
    
    pipeline = ETLPipeline()
    
    # Run once on startup
    pipeline.run_pipeline()
    
    # Schedule regular runs
    schedule.every(WEATHER_COLLECTION_INTERVAL).minutes.do(pipeline.run_pipeline)
    
    logger.info(f"Pipeline scheduled to run every {WEATHER_COLLECTION_INTERVAL} minutes")
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()