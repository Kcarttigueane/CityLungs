from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import logging
from prediction_service import PredictionService
from model_trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize services
prediction_service = PredictionService()
model_trainer = ModelTrainer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ml-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Generate PM2.5 predictions"""
    try:
        data = request.get_json()
        location = data.get('location')
        hours_ahead = data.get('hours_ahead', 24)
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Generate predictions
        predictions = prediction_service.predict(location, hours_ahead)
        
        return jsonify({
            'location': location,
            'predictions': predictions,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train_models():
    """Trigger model training"""
    try:
        data = request.get_json()
        location = data.get('location', 'all')
        
        # Run training in background (in production, use Celery or similar)
        result = model_trainer.train_all_models(location)
        
        return jsonify({
            'status': 'success',
            'models_trained': result['models_trained'],
            'metrics': result['metrics'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        models = prediction_service.get_available_models()
        return jsonify({
            'models': models,
            'count': len(models)
        })
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics/<model_name>', methods=['GET'])
def get_model_metrics(model_name):
    """Get metrics for a specific model"""
    try:
        metrics = model_trainer.get_model_metrics(model_name)
        if metrics:
            return jsonify(metrics)
        else:
            return jsonify({'error': 'Model not found'}), 404
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize the service
    logger.info("Starting ML service initialization...")
    try:
        from startup import initialize_ml_service
        initialize_ml_service()
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        logger.info("Continuing with service startup...")
    
    app.run(host='0.0.0.0', port=5000, debug=False)