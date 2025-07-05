#!/usr/bin/env python3
"""
Startup script for ML service to ensure proper initialization
"""

import os
import sys
import logging
from database import DatabaseConnection
from model_trainer import ModelTrainer
from prediction_service import PredictionService
from config import MODEL_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_ml_service():
    """Initialize the ML service with proper setup"""
    logger.info("Initializing ML service...")
    
    # Create models directory if it doesn't exist
    os.makedirs(MODEL_PATH, exist_ok=True)
    logger.info(f"Models directory: {MODEL_PATH}")
    
    # Test database connection
    try:
        db = DatabaseConnection()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    
    # Check if we have training data
    try:
        trainer = ModelTrainer()
        # Try to get some training data
        training_data = db.get_training_data(days=7)  # Try last 7 days
        if training_data.empty:
            logger.warning("No training data available in database")
            logger.info("Run data collection pipeline first to populate database")
        else:
            logger.info(f"Found {len(training_data)} training samples")
            
            # Train models for each location if we have sufficient data
            locations_with_data = training_data['location_name'].value_counts()
            for location, count in locations_with_data.items():
                if count >= 100:  # Minimum samples for training
                    logger.info(f"Training models for {location} ({count} samples)")
                    try:
                        result = trainer.train_all_models(location)
                        logger.info(f"Training completed for {location}")
                    except Exception as e:
                        logger.error(f"Training failed for {location}: {str(e)}")
                else:
                    logger.warning(f"Insufficient data for {location}: {count} samples")
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
    
    # Test prediction service
    try:
        pred_service = PredictionService()
        available_models = pred_service.get_available_models()
        logger.info(f"Available models: {len(available_models)}")
        for model in available_models:
            logger.info(f"  - {model['name']} ({model['type']})")
    except Exception as e:
        logger.error(f"Error initializing prediction service: {str(e)}")
    
    logger.info("ML service initialization completed")
    return True

if __name__ == "__main__":
    success = initialize_ml_service()
    if not success:
        sys.exit(1)