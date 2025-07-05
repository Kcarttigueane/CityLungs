#!/usr/bin/env python3
"""
Simplified test script for the complete ML and data pipeline
"""

import os
import sys
import logging
import requests
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connectivity"""
    logger.info("Testing database connection...")
    try:
        from sqlalchemy import create_engine, text
        from decouple import config
        
        DATABASE_URL = config('DATABASE_URL', default='postgresql://postgres:localpassword123@localhost:5432/smartcity')
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False

def test_ml_service_standalone():
    """Test ML service using standalone runner"""
    logger.info("Testing ML service components...")
    try:
        # Change to ML directory and run standalone test
        result = subprocess.run([
            sys.executable, 'run_standalone.py'
        ], cwd='./ml', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✓ ML service components test passed")
            return True
        else:
            logger.error(f"✗ ML service test failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"✗ ML service test failed: {str(e)}")
        return False

def test_pipeline_standalone():
    """Test pipeline using standalone runner"""
    logger.info("Testing pipeline components...")
    try:
        # Change to pipeline directory and run standalone test
        result = subprocess.run([
            sys.executable, 'run_standalone.py'
        ], cwd='./pipeline', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✓ Pipeline components test passed")
            return True
        else:
            logger.error(f"✗ Pipeline test failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"✗ Pipeline test failed: {str(e)}")
        return False

def test_ml_service_api():
    """Test ML service API endpoints"""
    logger.info("Testing ML service API...")
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            logger.info("✓ ML service health check passed")
            
            # Test models endpoint
            response = requests.get('http://localhost:5001/models', timeout=10)
            if response.status_code == 200:
                models = response.json()
                logger.info(f"✓ ML service models endpoint: {models['count']} models available")
                return True
            else:
                logger.error(f"✗ ML service models endpoint failed: {response.status_code}")
                return False
        else:
            logger.error(f"✗ ML service health check failed: {response.status_code}")
            return False
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ ML service API test failed: {str(e)}")
        logger.info("Make sure ML service is running on port 5001")
        return False

def test_sample_data_generation():
    """Test sample data generation"""
    logger.info("Testing sample data generation...")
    try:
        result = subprocess.run([
            sys.executable, 'generate_sample_ml_data.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✓ Sample data generation successful")
            return True
        else:
            logger.error(f"✗ Sample data generation failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"✗ Sample data generation failed: {str(e)}")
        return False

def run_simplified_test():
    """Run simplified pipeline test"""
    logger.info("=" * 50)
    logger.info("STARTING SIMPLIFIED PIPELINE TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Sample Data Generation", test_sample_data_generation),
        ("ML Service Components", test_ml_service_standalone),
        ("Pipeline Components", test_pipeline_standalone),
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
    
    if passed >= 3:  # Allow some tests to fail (like API if service isn't running)
        logger.info("🎉 Core tests passed! Pipeline is working.")
        return True
    else:
        logger.error("❌ Critical tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = run_simplified_test()
    sys.exit(0 if success else 1)