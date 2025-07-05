import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import logging
from database import DatabaseConnection
from feature_engineering import FeatureEngineer
from config import MODEL_PATH, FEATURE_COLUMNS

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.feature_engineer = FeatureEngineer()
        self.loaded_models = {}
        
    def predict(self, location, hours_ahead=24):
        """Generate predictions for specified location and time horizon"""
        try:
            # Get latest data (more hours to ensure we have enough for lag features)
            latest_data = self.db.get_latest_features(location, hours=48)
            
            if latest_data.empty:
                logger.error(f"No data available for {location}")
                return []
            
            # Create features
            features_df = self.feature_engineer.create_features(latest_data)
            
            # Get the latest row with all features
            if features_df.empty:
                logger.error(f"No features generated for {location}")
                return []
                
            latest_features = features_df.iloc[-1:].copy()
            
            # Load models for this location
            rf_model = self._load_model(f"rf_{location.replace(' ', '_').lower()}")
            xgb_model = self._load_model(f"xgb_{location.replace(' ', '_').lower()}")
            
            predictions = []
            current_time = latest_features['timestamp'].iloc[0]
            
            # Generate predictions for each hour
            for hour in range(1, hours_ahead + 1):
                target_time = current_time + timedelta(hours=hour)
                
                # Update time-based features
                pred_features = self._update_temporal_features(
                    latest_features.copy(), 
                    target_time
                )
                
                # Prepare features - only use available features
                available_features = [col for col in FEATURE_COLUMNS if col in pred_features.columns]
                if not available_features:
                    logger.warning(f"No features available for prediction at {location}")
                    continue
                    
                X = self.feature_engineer.prepare_for_prediction(
                    pred_features, 
                    available_features
                )
                
                # Make predictions with both models
                predictions_hour = []
                
                if rf_model and len(X) > 0:
                    try:
                        rf_pred = rf_model.predict(X)[0]
                        predictions_hour.append({
                            'timestamp': target_time.isoformat(),
                            'pm25': max(0, float(rf_pred)),  # Ensure non-negative predictions
                            'model': 'random_forest',
                            'confidence': self._calculate_confidence(rf_pred, 'random_forest')
                        })
                    except Exception as e:
                        logger.error(f"RF prediction failed: {str(e)}")
                
                if xgb_model and len(X) > 0:
                    try:
                        xgb_pred = xgb_model.predict(X)[0]
                        predictions_hour.append({
                            'timestamp': target_time.isoformat(),
                            'pm25': max(0, float(xgb_pred)),  # Ensure non-negative predictions
                            'model': 'xgboost',
                            'confidence': self._calculate_confidence(xgb_pred, 'xgboost')
                        })
                    except Exception as e:
                        logger.error(f"XGB prediction failed: {str(e)}")
                
                # Ensemble prediction
                if len(predictions_hour) >= 2:
                    ensemble_pred = np.mean([p['pm25'] for p in predictions_hour])
                    predictions_hour.append({
                        'timestamp': target_time.isoformat(),
                        'pm25': max(0, float(ensemble_pred)),  # Ensure non-negative predictions
                        'model': 'ensemble',
                        'confidence': self._calculate_confidence(ensemble_pred, 'ensemble')
                    })
                elif len(predictions_hour) == 1:
                    # If only one model available, mark it as ensemble
                    predictions_hour[0]['model'] = 'single_model'
                
                predictions.extend(predictions_hour)
                
                # Update lag features for next prediction
                if 'pm25' in latest_features.columns and len(predictions_hour) > 0:
                    # Use the best available prediction for lag features
                    best_pred = predictions_hour[-1]['pm25']  # Use last prediction (ensemble if available)
                    latest_features.loc[latest_features.index[-1], 'pm25_lag_1h'] = best_pred
            
            # Save predictions to database
            self._save_predictions(location, predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error for {location}: {str(e)}")
            return []
    
    def _load_model(self, model_name):
        """Load a trained model"""
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        model_path = os.path.join(MODEL_PATH, f"{model_name}.pkl")
        
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                self.loaded_models[model_name] = model
                logger.info(f"Loaded model: {model_name}")
                return model
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {str(e)}")
        else:
            logger.warning(f"Model not found: {model_name}")
        
        return None
    
    def _update_temporal_features(self, df, target_time):
        """Update temporal features for future prediction"""
        df['timestamp'] = target_time
        df['hour'] = target_time.hour
        df['day_of_week'] = target_time.weekday()
        df['month'] = target_time.month
        df['is_weekend'] = int(target_time.weekday() >= 5)
        
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * target_time.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * target_time.hour / 24)
        
        day_of_year = target_time.timetuple().tm_yday
        df['day_sin'] = np.sin(2 * np.pi * day_of_year / 365)
        df['day_cos'] = np.cos(2 * np.pi * day_of_year / 365)
        
        return df
    
    def _calculate_confidence(self, prediction, model_type):
        """Calculate confidence score for prediction"""
        # Simple confidence based on prediction value and model type
        # In production, use prediction intervals or model uncertainty
        base_confidence = 0.85
        
        if model_type == 'ensemble':
            base_confidence = 0.90
        elif model_type == 'xgboost':
            base_confidence = 0.87
        
        # Adjust based on prediction value (higher values = lower confidence)
        if prediction > 100:
            confidence = base_confidence * 0.8
        elif prediction > 50:
            confidence = base_confidence * 0.9
        else:
            confidence = base_confidence
        
        return round(confidence, 2)
    
    def _save_predictions(self, location, predictions):
        """Save predictions to database"""
        if not predictions:
            return
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(predictions)
            df['location_name'] = location
            df['prediction_timestamp'] = datetime.utcnow()
            df['target_timestamp'] = pd.to_datetime(df['timestamp'])
            df['predicted_pm25'] = df['pm25']
            df['confidence_score'] = df['confidence']
            df['model_name'] = df['model']
            
            # Select columns for database
            db_df = df[['location_name', 'prediction_timestamp', 'target_timestamp', 
                       'predicted_pm25', 'confidence_score', 'model_name']]
            
            # Save to database
            self.db.save_predictions(db_df)
            logger.info(f"Saved {len(predictions)} predictions for {location}")
        except Exception as e:
            logger.error(f"Error saving predictions: {str(e)}")
    
    def get_available_models(self):
        """List all available models"""
        models = []
        
        if os.path.exists(MODEL_PATH):
            for file in os.listdir(MODEL_PATH):
                if file.endswith('.pkl'):
                    model_name = file.replace('.pkl', '')
                    metrics_file = f"{model_name}_metrics.json"
                    has_metrics = os.path.exists(
                        os.path.join(MODEL_PATH, metrics_file)
                    )
                    
                    models.append({
                        'name': model_name,
                        'type': 'random_forest' if model_name.startswith('rf_') else 'xgboost',
                        'has_metrics': has_metrics,
                        'file': file
                    })
        
        return models