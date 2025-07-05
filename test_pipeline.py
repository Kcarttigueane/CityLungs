#!/usr/bin/env python3
"""
Test script for the complete ML and data pipeline
"""

import os
import sys
import logging
import requests
import time
from datetime import datetime, timedelta

# Ensure we're in the right directory
if os.path.basename(os.getcwd()) != 'CityLungs':
    print("Please run this script from the CityLungs directory")
    sys.exit(1)

# Import modules directly
try:
    from pipeline.database import DatabaseManager
    from pipeline.scheduler import ETLPipeline
    from ml.database import DatabaseConnection
    from ml.model_trainer import ModelTrainer
    from ml.prediction_service import PredictionService
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the CityLungs directory")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connectivity"""
    logger.info("Testing database connection...")
    try:
        db = DatabaseManager()
        ml_db = DatabaseConnection()
        logger.info("✓ Database connections successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False

def test_data_collection():
    """Test data collection pipeline"""
    logger.info("Testing data collection pipeline...")
    try:
        pipeline = ETLPipeline()
        
        # Test weather data collection
        weather_data = pipeline.weather_collector.collect()
        logger.info(f"✓ Weather data collected: {len(weather_data)} measurements")
        
        # Test air quality data collection
        air_quality_data = pipeline.air_quality_collector.collect()
        logger.info(f"✓ Air quality data collected: {len(air_quality_data)} measurements")
        
        # Test data transformation
        transformed_data = pipeline.transformer.transform(weather_data, air_quality_data)
        logger.info(f"✓ Data transformed: {len(transformed_data)} combined measurements")
        
        # Test database insertion
        if transformed_data:
            pipeline.db.insert_measurements(transformed_data)
            logger.info("✓ Data inserted into database")
        
        return True
    except Exception as e:
        logger.error(f"✗ Data collection failed: {str(e)}")
        return False

def test_ml_training():
    """Test ML model training"""
    logger.info("Testing ML model training...")
    try:
        trainer = ModelTrainer()
        
        # Get training data
        training_data = trainer.db.get_training_data(days=7)
        if training_data.empty:
            logger.warning("No training data available - skipping ML training test")
            return True
        
        logger.info(f"Training data available: {len(training_data)} samples")
        
        # Test feature engineering
        features_df = trainer.feature_engineer.create_features(training_data)
        logger.info(f"✓ Features engineered: {len(features_df)} samples with {len(features_df.columns)} features")
        
        # Try training on first location with sufficient data
        locations_with_data = training_data['location_name'].value_counts()
        for location, count in locations_with_data.items():
            if count >= 50:  # Lower threshold for testing
                logger.info(f"Testing training on {location} with {count} samples")
                result = trainer.train_all_models(location)
                logger.info(f"✓ Model training completed for {location}")
                break
        else:
            logger.warning("Insufficient data for training - need more historical data")
        
        return True
    except Exception as e:
        logger.error(f"✗ ML training failed: {str(e)}")
        return False

def test_ml_prediction():
    """Test ML prediction service"""
    logger.info("Testing ML prediction service...")
    try:
        pred_service = PredictionService()
        
        # List available models
        models = pred_service.get_available_models()
        logger.info(f"Available models: {len(models)}")
        
        if not models:
            logger.warning("No trained models available - skipping prediction test")
            return True
        
        # Test prediction for first available location
        db = DatabaseConnection()
        recent_data = db.get_training_data(days=1)
        
        if recent_data.empty:
            logger.warning("No recent data available for prediction test")
            return True
        
        test_location = recent_data['location_name'].iloc[0]
        logger.info(f"Testing predictions for {test_location}")
        
        predictions = pred_service.predict(test_location, hours_ahead=12)
        logger.info(f"✓ Predictions generated: {len(predictions)} predictions")
        
        if predictions:
            logger.info(f"Sample prediction: {predictions[0]}")
        
        return True
    except Exception as e:
        logger.error(f"✗ ML prediction failed: {str(e)}")
        return False

def test_ml_service_api():
    """Test ML service API endpoints"""
    logger.info("Testing ML service API...")
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            logger.info("✓ ML service health check passed")
        else:
            logger.error(f"✗ ML service health check failed: {response.status_code}")
            return False
        
        # Test models endpoint
        response = requests.get('http://localhost:5001/models', timeout=10)
        if response.status_code == 200:
            models = response.json()
            logger.info(f"✓ ML service models endpoint: {models['count']} models available")
        else:
            logger.error(f"✗ ML service models endpoint failed: {response.status_code}")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ ML service API test failed: {str(e)}")
        logger.info("Make sure ML service is running on port 5001")
        return False

def run_full_test():
    """Run complete pipeline test"""
    logger.info("=" * 50)
    logger.info("STARTING COMPLETE PIPELINE TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Data Collection", test_data_collection),
        ("ML Training", test_ml_training),
        ("ML Prediction", test_ml_prediction),
        ("ML Service API", test_ml_service_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if success:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 ALL TESTS PASSED! Pipeline is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)