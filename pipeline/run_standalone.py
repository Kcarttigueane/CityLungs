#!/usr/bin/env python3
"""
Standalone runner for pipeline components
"""

import os
import sys
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with absolute imports
import database
import scheduler
from collectors import openaq, openweather
from transformers import data_transformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test pipeline components"""
    logger.info("Testing pipeline components...")
    
    try:
        # Test database
        db = database.DatabaseManager()
        logger.info("✓ Database manager initialized")
        
        # Test collectors
        weather_collector = openweather.OpenWeatherCollector()
        air_quality_collector = openaq.OpenAQCollector()
        logger.info("✓ Data collectors initialized")
        
        # Test transformer
        transformer = data_transformer.DataTransformer()
        logger.info("✓ Data transformer initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ Pipeline test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)