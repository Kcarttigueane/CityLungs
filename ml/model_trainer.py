import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import json
import os
from datetime import datetime
import logging
from database import DatabaseConnection
from feature_engineering import FeatureEngineer
from config import MODEL_PATH, FEATURE_COLUMNS, RANDOM_FOREST_PARAMS, XGBOOST_PARAMS

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.metrics = {}
        
    def train_all_models(self, location='all'):
        """Train all models for specified location(s)"""
        logger.info(f"Starting model training for location: {location}")
        
        # Fetch training data
        df = self.db.get_training_data(location)
        
        if df.empty:
            logger.error("No training data available")
            return {'status': 'error', 'message': 'No training data'}
        
        # Create features
        df = self.feature_engineer.create_features(df)
        
        # Train models for each location
        locations = df['location_name'].unique() if location == 'all' else [location]
        trained_models = []
        
        for loc in locations:
            logger.info(f"Training models for {loc}")
            loc_df = df[df['location_name'] == loc].copy()
            
            # Train Random Forest
            rf_metrics = self._train_random_forest(loc_df, loc)
            
            # Train XGBoost
            xgb_metrics = self._train_xgboost(loc_df, loc)
            
            trained_models.append({
                'location': loc,
                'models': ['random_forest', 'xgboost'],
                'metrics': {
                    'random_forest': rf_metrics,
                    'xgboost': xgb_metrics
                }
            })
        
        result = {
            'status': 'success',
            'models_trained': trained_models,
            'metrics': self.metrics
        }
        
        logger.info(f"Training completed. Result: {result}")
        return result
    
    def _train_random_forest(self, df, location):
        """Train Random Forest model"""
        # Prepare data - only keep rows with pm25 values
        df_clean = df.dropna(subset=['pm25']).copy()
        
        if len(df_clean) < 100:
            logger.warning(f"Insufficient data for {location}: {len(df_clean)} samples")
            return None
        
        # Select only available features
        available_features = [col for col in FEATURE_COLUMNS if col in df_clean.columns]
        missing_features = [col for col in FEATURE_COLUMNS if col not in df_clean.columns]
        
        if missing_features:
            logger.info(f"Missing features for {location}: {missing_features}")
        
        # Fill missing values for available features
        for col in available_features:
            if df_clean[col].isna().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        
        X = df_clean[available_features]
        y = df_clean['pm25']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(**RANDOM_FOREST_PARAMS)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_absolute_error')
        metrics['cv_mae'] = -cv_scores.mean()
        
        # Save model
        model_name = f"rf_{location.replace(' ', '_').lower()}"
        model_path = os.path.join(MODEL_PATH, f"{model_name}.pkl")
        joblib.dump(model, model_path)
        
        # Save metrics
        self.metrics[model_name] = metrics
        self._save_metrics(model_name, metrics)
        
        logger.info(f"Random Forest trained for {location}: MAE={metrics['mae']:.2f}")
        
        return metrics
    
    def _train_xgboost(self, df, location):
        """Train XGBoost model"""
        # Prepare data - only keep rows with pm25 values
        df_clean = df.dropna(subset=['pm25']).copy()
        
        if len(df_clean) < 100:
            logger.warning(f"Insufficient data for {location}: {len(df_clean)} samples")
            return None
        
        # Select only available features
        available_features = [col for col in FEATURE_COLUMNS if col in df_clean.columns]
        missing_features = [col for col in FEATURE_COLUMNS if col not in df_clean.columns]
        
        if missing_features:
            logger.info(f"Missing features for {location}: {missing_features}")
        
        # Fill missing values for available features
        for col in available_features:
            if df_clean[col].isna().any():
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        
        X = df_clean[available_features]
        y = df_clean['pm25']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = xgb.XGBRegressor(**XGBOOST_PARAMS)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=10,
            verbose=False
        )
        
        # Evaluate
        y_pred = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': available_features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        metrics['top_features'] = importance.head(10).to_dict('records')
        
        # Save model
        model_name = f"xgb_{location.replace(' ', '_').lower()}"
        model_path = os.path.join(MODEL_PATH, f"{model_name}.pkl")
        joblib.dump(model, model_path)
        
        # Save metrics
        self.metrics[model_name] = metrics
        self._save_metrics(model_name, metrics)
        
        logger.info(f"XGBoost trained for {location}: MAE={metrics['mae']:.2f}")
        
        return metrics
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate regression metrics"""
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            'samples': len(y_true),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _save_metrics(self, model_name, metrics):
        """Save metrics to file"""
        metrics_path = os.path.join(MODEL_PATH, f"{model_name}_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def get_model_metrics(self, model_name):
        """Get metrics for a specific model"""
        metrics_path = os.path.join(MODEL_PATH, f"{model_name}_metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                return json.load(f)
        return None
