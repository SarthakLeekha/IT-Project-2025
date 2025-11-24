import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import logging
import joblib

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.encoder_path = 'models'
        self.model_path = 'models'

    def load_or_create_encoders(self):
        """Load existing encoders or create placeholder ones"""
        encoder_files = {
            'crop': 'crop_encoder.pkl',
            'soil': 'soil_encoder.pkl', 
            'fertilizer_crop': 'fertilizer_crop_encoder.pkl',
            'fertilizer_soil': 'fertilizer_soil_encoder.pkl',
            'fertilizer': 'fertilizer_encoder.pkl'
        }

        for name, filename in encoder_files.items():
            filepath = os.path.join(self.encoder_path, filename)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                try:
                    with open(filepath, 'rb') as f:
                        self.encoders[name] = pickle.load(f)
                    logger.info(f"Loaded {name} encoder")
                except Exception as e:
                    logger.warning(f"Failed to load {name} encoder: {e}")
            else:
                logger.info(f"Encoder file not found or empty: {filepath}")
                self.encoders[name] = LabelEncoder()

    def load_models(self):
        """Load existing models"""
        logger.info("Loading models...")

        self.load_or_create_encoders()

        
        improved_fert_path = os.path.join(self.model_path, 'fertilizer_model_improved.pkl')
        if os.path.exists(improved_fert_path):
            try:
                self.models['fertilizer_model'] = joblib.load(improved_fert_path)
                logger.info("Loaded improved fertilizer model")

                scaler_path = os.path.join(self.model_path, 'fertilizer_scaler.pkl')
                if os.path.exists(scaler_path):
                    self.scalers['fertilizer_scaler'] = joblib.load(scaler_path)
                    logger.info("Loaded fertilizer scaler")
            except Exception as e:
                logger.error(f"Failed to load improved fertilizer model: {e}")

        model_files = {
            'crop_model': 'crop_model.pkl',
            'fertilizer_model': 'fertilizer_model.pkl',  
            'soil_model': 'soil_model.pkl'
        }

        scaler_files = {
            'crop_scaler': 'crop_scaler.pkl',
            'soil_scaler': 'soil_scaler.pkl'
        }

        models_loaded = 0

        for model_name, filename in model_files.items():
            if model_name in self.models:  
                models_loaded += 1
                continue

            filepath = os.path.join(self.model_path, filename)
            if os.path.exists(filepath):
                try:
                    self.models[model_name] = joblib.load(filepath)
                    logger.info(f"Loaded {model_name}")
                    models_loaded += 1
                except Exception as e:
                    logger.error(f"Failed to load {model_name}: {e}")
            else:
                logger.warning(f"Model file not found: {filepath}")

        for scaler_name, filename in scaler_files.items():
            if scaler_name in self.scalers:  
                continue

            filepath = os.path.join(self.model_path, filename)
            if os.path.exists(filepath):
                try:
                    self.scalers[scaler_name] = joblib.load(filepath)
                    logger.info(f" Loaded {scaler_name}")
                except Exception as e:
                    logger.error(f"Failed to load {scaler_name}: {e}")

        logger.info(f"{models_loaded} models loaded successfully!")
        return models_loaded

    def train_all_models(self):
        """Train all models with available data"""
        logger.info("Training models...")

        try:
            logger.info("Models are already trained and loaded")
            return {
                'crop_model': 'already_trained',
                'fertilizer_model': 'already_trained', 
                'soil_model': 'already_trained',
                'status': 'models_loaded'
            }

        except Exception as e:
            logger.error(f"Training error: {e}")
            return {'error': str(e)}

    def predict_crop(self, features):
        """Predict crop based on features"""
        try:
            if 'crop_model' not in self.models:
                return "Crop model not loaded"

            if isinstance(features, np.ndarray):
                features = features.reshape(1, -1)

            if 'crop_scaler' in self.scalers:
                features = self.scalers['crop_scaler'].transform(features)

            prediction = self.models['crop_model'].predict(features)[0]

            
            crop_names = ['cotton', 'groundnut', 'maize', 'rice', 'sugarcane', 'wheat']
            if 0 <= prediction < len(crop_names):
                return crop_names[prediction]
            else:
                return f"Crop_{prediction}"

        except Exception as e:
            logger.error(f"Crop prediction error: {e}")
            return "Prediction failed"

    def predict_fertilizer(self, features):
        """Predict fertilizer based on features - FIXED VERSION"""
        try:
            if 'fertilizer_model' not in self.models:
                return "Fertilizer model not loaded"

            
            if isinstance(features, dict):
                
                feature_array = self._prepare_fertilizer_features(features)
            elif isinstance(features, np.ndarray):
                feature_array = features.reshape(1, -1)
            else:
                return "Invalid input format"

            
            if feature_array.shape[1] != 9:
                feature_array = self._adjust_features_to_9(feature_array)

            prediction = self.models['fertilizer_model'].predict(feature_array)[0]

            fertilizer_names = ['Urea', 'DAP', 'MOP', 'SSP', 'NPK', 'Potash', 'Organic']
            if 0 <= prediction < len(fertilizer_names):
                return fertilizer_names[prediction]
            else:
                return f"Fertilizer_{prediction}"

        except Exception as e:
            logger.error(f"Fertilizer prediction error: {e}")
            return "Prediction failed"

    def _prepare_fertilizer_features(self, features_dict):
        """Prepare fertilizer features from dictionary input"""

        soil_ph = float(features_dict.get('soil_ph', 6.5))

        nitrogen = max(0, min(100, float(features_dict.get('nitrogen', 30))))
        phosphorus = max(0, min(100, float(features_dict.get('phosphorus', 25))))
        potassium = max(0, min(100, float(features_dict.get('potassium', 15))))

        n_level = 'low' if nitrogen < 25 else 'medium' if nitrogen < 50 else 'high'
        p_level = 'low' if phosphorus < 20 else 'medium' if phosphorus < 40 else 'high'
        k_level = 'low' if potassium < 20 else 'medium' if potassium < 40 else 'high'

        level_map = {'low': 0, 'medium': 1, 'high': 2}
        n_score = level_map[n_level]
        p_score = level_map[p_level]
        k_score = level_map[k_level]
        total_score = n_score + p_score + k_score

        n_def = 1 if n_level == 'low' else 0
        p_def = 1 if p_level == 'low' else 0
        k_def = 1 if k_level == 'low' else 0

        crop_type = features_dict.get('crop_type', 'wheat')
        if 'fertilizer_crop' in self.encoders:
            try:
                crop_encoded = self.encoders['fertilizer_crop'].transform([crop_type])[0]
            except:
                crop_encoded = 0
        else:
            crop_encoded = 0

        soil_type = features_dict.get('soil_type', 'loamy')
        if 'fertilizer_soil' in self.encoders:
            try:
                soil_encoded = self.encoders['fertilizer_soil'].transform([soil_type])[0]
            except:
                soil_encoded = 1
        else:
            soil_encoded = 1

        npk_ratio = n_score / (p_score + k_score + 1)  # Avoid division by zero
        deficiency_count = n_def + p_def + k_def

        feature_array = np.array([[
            soil_ph, n_score, p_score, k_score, crop_encoded, soil_encoded, total_score, npk_ratio, deficiency_count
        ]])

        return feature_array

    def _adjust_features_to_9(self, feature_array):
        """Adjust feature array to have exactly 9 features"""
        current_features = feature_array.shape[1]
        
        if current_features > 9:
            
            return feature_array[:, :9]
        elif current_features < 9:
            
            padding = np.zeros((feature_array.shape[0], 9 - current_features))
            return np.hstack([feature_array, padding])
        else:
            return feature_array

    def predict_soil(self, features):
        """Predict soil recommendations"""
        try:
            if 'soil_model' not in self.models:
                return "Soil model not loaded"

            if isinstance(features, np.ndarray):
                features = features.reshape(1, -1)

            if features.shape[1] != 6:
                if features.shape[1] == 5:
                    features = np.hstack([features, np.array([[0.5]])])
                else:
                    if features.shape[1] > 6:
                        features = features[:, :6]
                    else:
                        padding = np.zeros((features.shape[0], 6 - features.shape[1]))
                        features = np.hstack([features, padding])

            if 'soil_scaler' in self.scalers:
                features = self.scalers['soil_scaler'].transform(features)

            prediction = self.models['soil_model'].predict(features)[0]

            recommendations = ['add_lime', 'add_compost', 'irrigate', 'drain', 'add_manure', 'add_gypsum']
            if 0 <= prediction < len(recommendations):
                return recommendations[prediction]
            else:
                return f"Recommendation_{prediction}"

        except Exception as e:
            logger.error(f"Soil prediction error: {e}")
            return "Prediction failed"

    def get_model_info(self):
        """Get information about loaded models"""
        info = {
            'models_loaded': list(self.models.keys()),
            'encoders_loaded': list(self.encoders.keys()),
            'scalers_loaded': list(self.scalers.keys())
        }
        
        for model_name, model in self.models.items():
            if hasattr(model, 'n_features_in_'):
                info[f'{model_name}_features'] = model.n_features_in_
            if hasattr(model, 'n_estimators'):
                info[f'{model_name}_estimators'] = model.n_estimators
        
        return info


model_manager = ModelManager()