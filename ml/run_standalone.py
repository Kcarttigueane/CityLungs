#!/usr/bin/env python3
"""
Standalone runner for ML service components
"""

import os
import sys
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with absolute imports
import database
import model_trainer
import prediction_service
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ml_service():
    """Test ML service components"""
    logger.info("Testing ML service components...")
    
    try:
        # Test database connection
        db = database.DatabaseConnection()
        logger.info("✓ Database connection successful")
        
        # Test model trainer
        trainer = model_trainer.ModelTrainer()
        logger.info("✓ Model trainer initialized")
        
        # Test prediction service
        pred_service = prediction_service.PredictionService()
        logger.info("✓ Prediction service initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ ML service test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ml_service()
    sys.exit(0 if success else 1)