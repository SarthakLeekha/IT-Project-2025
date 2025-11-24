
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime
import json
try:
    from backend.weather_service import get_weather_data, get_weather_forecast, get_agricultural_advice
except ImportError:
    from weather_service import get_weather_data, get_weather_forecast, get_agricultural_advice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'agriculture-secret-key-2024'
app.config['DEBUG'] = True
app.config['DISABLE_AUTH'] = True  

def load_actual_data():
    """Load actual data to get real crop and soil types"""
    try:
        fert_data = pd.read_csv('data/fertilizer_data.csv')
        crop_data = pd.read_csv('data/crop_data.csv')

        return {
            'crop_types': sorted(fert_data['crop_type'].unique()),
            'soil_types': sorted(fert_data['soil_type'].unique()),
            'fertilizers': sorted(fert_data['fertilizer_type'].unique()),
            'crops': sorted(crop_data['label'].unique())
        }
    except Exception as e:
        logger.warning(f"Could not load actual data: {e}")
        return {
            'crop_types': ['wheat', 'rice', 'maize', 'cotton', 'groundnut', 'barley', 'sugarcane'],
            'soil_types': ['clay', 'sandy', 'loamy', 'silt', 'black'],
            'fertilizers': ['Urea', 'DAP', 'NPK', 'Potash', 'Organic', 'MOP', 'SSP', '14-35-14'],
            'crops': ['maize', 'wheat', 'groundnut', 'rice', 'cotton']
        }

actual_data = load_actual_data()

datasets_info = {
    'fertilizer': {
        'features': {
            'crop_type': {'type': 'categorical', 'required': True, 'options': actual_data['crop_types']},
            'soil_type': {'type': 'categorical', 'required': True, 'options': actual_data['soil_types']},
            'nitrogen': {'type': 'numeric', 'required': True, 'min': 0, 'max': 100, 'description': 'Nitrogen level in soil'},
            'phosphorus': {'type': 'numeric', 'required': True, 'min': 0, 'max': 100, 'description': 'Phosphorus level in soil'},
            'potassium': {'type': 'numeric', 'required': True, 'min': 0, 'max': 100, 'description': 'Potassium level in soil'},
            'soil_ph': {'type': 'numeric', 'required': False, 'min': 4, 'max': 9, 'default': 6.5, 'description': 'Soil pH level'}
        },
        'target_values': actual_data['fertilizers'],
        'statistics': {'samples': '105+', 'features': '9', 'accuracy': '4.76%'}
    },
    'crop': {
        'features': {
            'N': {'type': 'numeric', 'required': True, 'min': 0, 'max': 150, 'description': 'Nitrogen content'},
            'P': {'type': 'numeric', 'required': True, 'min': 0, 'max': 150, 'description': 'Phosphorus content'},
            'K': {'type': 'numeric', 'required': True, 'min': 0, 'max': 200, 'description': 'Potassium content'},
            'temperature': {'type': 'numeric', 'required': True, 'min': 0, 'max': 50, 'description': 'Temperature in Celsius'},
            'humidity': {'type': 'numeric', 'required': True, 'min': 0, 'max': 100, 'description': 'Humidity percentage'},
            'ph': {'type': 'numeric', 'required': True, 'min': 3, 'max': 10, 'description': 'Soil pH'},
            'rainfall': {'type': 'numeric', 'required': True, 'min': 0, 'max': 300, 'description': 'Rainfall in mm'}
        },
        'target_values': actual_data['crops'],
        'statistics': {'samples': '2200', 'crops': '6', 'accuracy': '99%+'}
    }
}

class AgriculturePredictor:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.load_models()

    def load_models(self):
        """Load all trained models"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'ml_models.joblib')
            encoder_path = os.path.join(os.path.dirname(__file__), 'models', 'label_encoders.joblib')
            self.models = joblib.load(model_path)
            self.encoders = joblib.load(encoder_path)
            logger.info("All models loaded successfully")
            logger.info(f"Available models: {list(self.models.keys())}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models = {}
            self.encoders = {}

    def predict_fertilizer(self, features):
        """Predict fertilizer based on soil and crop conditions - IMPROVED VERSION"""
        try:
            print("Debug: Starting fertilizer prediction")
            if 'fertilizer_recommendation' not in self.models:
                return {"success": False, "error": "Fertilizer model not available"}

            crop_type = features.get('crop_type', '').lower().strip()
            soil_type = features.get('soil_type', '').lower().strip()

            if crop_type not in [c.lower() for c in actual_data['crop_types']]:
                return {"success": False, "error": f"Invalid crop type. Available: {actual_data['crop_types']}"}

            if soil_type not in [s.lower() for s in actual_data['soil_types']]:
                return {"success": False, "error": f"Invalid soil type. Available: {actual_data['soil_types']}"}

            try:
                nitrogen = max(0, min(100, float(features.get('nitrogen', 30))))
                phosphorus = max(0, min(100, float(features.get('phosphorus', 25))))
                potassium = max(0, min(100, float(features.get('potassium', 15))))
                soil_ph = max(4, min(9, float(features.get('soil_ph', 6.5))))
            except (ValueError, TypeError) as e:
                return {"success": False, "error": f"Invalid numeric values: {e}"}

            logger.info(f" Predicting fertilizer for {crop_type} in {soil_type} soil")
            logger.info(f"   Nutrients - N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{soil_ph}")

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

            
            crop_encoded = 0
            soil_encoded = 0

            try:
                from backend.model_manager import model_manager
                if hasattr(model_manager, 'encoders') and 'fertilizer_crop' in model_manager.encoders:
                    crop_encoded = model_manager.encoders['fertilizer_crop'].transform([crop_type])[0]
                if hasattr(model_manager, 'encoders') and 'fertilizer_soil' in model_manager.encoders:
                    soil_encoded = model_manager.encoders['fertilizer_soil'].transform([soil_type])[0]
            except:
                
                crop_encoded = hash(crop_type) % 7
                soil_encoded = hash(soil_type) % 4

            
            npk_ratio = n_score / (p_score + k_score + 1)  
            deficiency_count = n_def + p_def + k_def

            
            model = self.models['fertilizer_recommendation']

            
            if hasattr(model, 'n_features_in_') and model.n_features_in_ == 9:
                
                features_array = np.array([[
                    soil_ph, n_score, p_score, k_score, crop_encoded, soil_encoded,
                    total_score, npk_ratio, deficiency_count
                ]])

                
                try:
                    from backend.model_manager import model_manager
                    if 'fertilizer_scaler' in model_manager.scalers:
                        features_array = model_manager.scalers['fertilizer_scaler'].transform(features_array)
                except:
                    pass  
            else:
                
                features_array = np.array([[
                    soil_ph, n_score, p_score, k_score, total_score,
                    n_def, p_def, k_def, soil_encoded
                ]])

            logger.info(f" Using {features_array.shape[1]} features for prediction")

            pred_encoded = model.predict(features_array)[0]
            fertilizer = self.encoders['fertilizer_type'].inverse_transform([pred_encoded])[0]

            probabilities = model.predict_proba(features_array)[0]
            confidence = float(probabilities[pred_encoded])

            recommendation = self._generate_recommendation(fertilizer, n_level, p_level, k_level)

            return {
                "success": True,
                "fertilizer": fertilizer,
                "confidence": round(confidence, 3),
                "recommendation": recommendation,
                "nutrient_analysis": {
                    "nitrogen": {"level": n_level, "value": nitrogen, "deficient": n_def},
                    "phosphorus": {"level": p_level, "value": phosphorus, "deficient": p_def},
                    "potassium": {"level": k_level, "value": potassium, "deficient": k_def}
                },
                "soil_info": {
                    "type": soil_type,
                    "ph": soil_ph,
                    "status": "optimal" if 6.0 <= soil_ph <= 7.5 else "needs adjustment"
                }
            }

        except Exception as e:
            logger.error(f" Fertilizer prediction error: {e}")
            return {"success": False, "error": f"Prediction failed: {str(e)}"}

    def _generate_recommendation(self, fertilizer, n_level, p_level, k_level):
        """Generate human-readable recommendation"""
        recommendations = {
            'Urea': 'Apply Urea for nitrogen deficiency. Best for vegetative growth.',
            'DAP': 'Use DAP for balanced nitrogen and phosphorus. Good for early growth.',
            'NPK': 'NPK provides balanced nutrition. Ideal for most crops.',
            'Potash': 'Potash addresses potassium deficiency. Improves fruit quality.',
            'Organic': 'Organic manure improves soil health. Good for long-term fertility.',
            'MOP': 'MOP for potassium deficiency. Enhances disease resistance.',
            'SSP': 'SSP provides phosphorus. Good for root development.',
            '14-35-14': 'Complex fertilizer for specific crop needs.'
        }

        base_msg = recommendations.get(fertilizer, f"Use {fertilizer} for your crop.")

        nutrient_advice = []
        if n_level == 'low':
            nutrient_advice.append("Nitrogen is low - promotes leaf growth")
        if p_level == 'low':
            nutrient_advice.append("Phosphorus is low - important for roots and flowers")
        if k_level == 'low':
            nutrient_advice.append("Potassium is low - helps with overall plant health")

        if nutrient_advice:
            base_msg += " " + ". ".join(nutrient_advice) + "."

        return base_msg

    def predict_crop(self, features):
        """Predict suitable crop based on soil conditions"""
        try:
            if 'crop_recommendation' not in self.models:
                return {"success": False, "error": "Crop model not available"}

            N = float(features.get('N', 50))
            P = float(features.get('P', 50))
            K = float(features.get('K', 50))
            temperature = float(features.get('temperature', 25))
            humidity = float(features.get('humidity', 60))
            ph = float(features.get('ph', 6.5))
            rainfall = float(features.get('rainfall', 100))

            features_array = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

            model = self.models['crop_recommendation']
            pred_encoded = model.predict(features_array)[0]
            crop = self.encoders['crop_label'].inverse_transform([pred_encoded])[0]

            return {
                "success": True,
                "crop": crop,
                "conditions": {
                    "N": N, "P": P, "K": K,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall
                }
            }

        except Exception as e:
            logger.error(f"Crop prediction error: {e}")
            return {"success": False, "error": f"Crop prediction failed: {str(e)}"}

    def analyze_soil(self, features):
        """Analyze soil health and provide recommendations"""
        try:
            N = float(features.get('N', 50))
            P = float(features.get('P', 50))
            K = float(features.get('K', 50))
            ph = float(features.get('ph', 6.5))
            organic_carbon = float(features.get('organic_carbon', 1.5))
            moisture = float(features.get('moisture', 25))
            soil_type = features.get('soil_type', 'loamy').lower()

            logger.info(f" Analyzing soil: N={N}, P={P}, K={K}, pH={ph}, OC={organic_carbon}, Moisture={moisture}, Type={soil_type}")

            nutrient_analysis = self._analyze_nutrients(N, P, K, ph, organic_carbon, moisture)

            health_score = self._calculate_soil_health_score(nutrient_analysis, ph, organic_carbon, moisture)

            recommendations = self._generate_soil_recommendations(nutrient_analysis, ph, organic_carbon, moisture, soil_type)

            return {
                "success": True,
                "soil_health_score": health_score,
                "fertility_level": self._get_fertility_level(health_score),
                "nutrients": nutrient_analysis,
                "recommendations": recommendations,
                "soil_info": {
                    "type": soil_type,
                    "ph": ph,
                    "organic_carbon": organic_carbon,
                    "moisture": moisture,
                    "ph_status": "optimal" if 6.0 <= ph <= 7.5 else "needs adjustment" if ph < 6.0 else "alkaline"
                }
            }

        except Exception as e:
            logger.error(f"Soil analysis error: {e}")
            return {"success": False, "error": f"Soil analysis failed: {str(e)}"}

    def _analyze_nutrients(self, N, P, K, ph, organic_carbon, moisture):
        """Analyze individual nutrient levels"""
        nutrient_ranges = {
            'N': {'low': (0, 30), 'medium': (30, 60), 'high': (60, 150)},
            'P': {'low': (0, 25), 'medium': (25, 50), 'high': (50, 150)},
            'K': {'low': (0, 30), 'medium': (30, 70), 'high': (70, 200)}
        }

        def get_level(value, ranges):
            if value <= ranges['low'][1]:
                return 'low'
            elif value <= ranges['medium'][1]:
                return 'medium'
            else:
                return 'high'

        def get_percentage(value, nutrient):
            max_val = nutrient_ranges[nutrient]['high'][1]
            return min(100, (value / max_val) * 100)

        return {
            'N': {
                'value': N,
                'level': get_level(N, nutrient_ranges['N']),
                'percentage': get_percentage(N, 'N')
            },
            'P': {
                'value': P,
                'level': get_level(P, nutrient_ranges['P']),
                'percentage': get_percentage(P, 'P')
            },
            'K': {
                'value': K,
                'level': get_level(K, nutrient_ranges['K']),
                'percentage': get_percentage(K, 'K')
            }
        }

    def _calculate_soil_health_score(self, nutrients, ph, organic_carbon, moisture):
        """Calculate overall soil health score (0-100)"""
        score = 0

        nutrient_score = 0
        for nutrient in ['N', 'P', 'K']:
            level = nutrients[nutrient]['level']
            if level == 'high':
                nutrient_score += 100
            elif level == 'medium':
                nutrient_score += 70
            else:  
                nutrient_score += 30
        nutrient_score = nutrient_score / 3
        score += nutrient_score * 0.4

        if 6.0 <= ph <= 7.5:
            ph_score = 100
        elif 5.5 <= ph < 6.0 or 7.5 < ph <= 8.0:
            ph_score = 70
        elif 5.0 <= ph < 5.5 or 8.0 < ph <= 8.5:
            ph_score = 40
        else:
            ph_score = 20
        score += ph_score * 0.25

        if organic_carbon >= 2.0:
            oc_score = 100
        elif organic_carbon >= 1.5:
            oc_score = 80
        elif organic_carbon >= 1.0:
            oc_score = 60
        elif organic_carbon >= 0.5:
            oc_score = 40
        else:
            oc_score = 20
        score += oc_score * 0.2

        if 20 <= moisture <= 40:
            moisture_score = 100
        elif 15 <= moisture < 20 or 40 < moisture <= 50:
            moisture_score = 70
        elif 10 <= moisture < 15 or 50 < moisture <= 60:
            moisture_score = 40
        else:
            moisture_score = 20
        score += moisture_score * 0.15

        return round(min(100, max(0, score)), 1)

    def _get_fertility_level(self, score):
        """Convert score to fertility level"""
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"

    def _generate_soil_recommendations(self, nutrients, ph, organic_carbon, moisture, soil_type):
        """Generate soil improvement recommendations"""
        recommendations = []

        if ph < 6.0:
            recommendations.append("Add lime to increase soil pH and improve nutrient availability")
        elif ph > 7.5:
            recommendations.append("Add organic matter or sulfur to decrease soil pH")

        if nutrients['N']['level'] == 'low':
            recommendations.append("Apply nitrogen-rich fertilizers like urea or ammonium nitrate")
        if nutrients['P']['level'] == 'low':
            recommendations.append("Add phosphorus fertilizers like DAP or rock phosphate")
        if nutrients['K']['level'] == 'low':
            recommendations.append("Use potassium fertilizers like MOP or potash")

        if organic_carbon < 1.5:
            recommendations.append("Incorporate organic matter like compost or manure to improve soil structure")

        if moisture < 20:
            recommendations.append("Improve irrigation practices to maintain adequate soil moisture")
        elif moisture > 40:
            recommendations.append("Improve drainage to prevent waterlogging")

        soil_recommendations = {
            'sandy': ["Add organic matter regularly to improve water retention", "Use split fertilizer applications"],
            'clay': ["Improve drainage and aeration", "Add gypsum to improve soil structure"],
            'loamy': ["Maintain current good soil structure", "Regular soil testing recommended"],
            'silt': ["Prevent soil compaction", "Add organic matter for better structure"]
        }

        if soil_type in soil_recommendations:
            recommendations.extend(soil_recommendations[soil_type])

        recommendations.extend([
            "Test soil annually to monitor changes",
            "Practice crop rotation to maintain soil fertility",
            "Use cover crops to prevent soil erosion"
        ])

        return recommendations[:8]  

my_predictor = AgriculturePredictor()

mock_users = {
    'farmer': {'password': 'agrio123', 'name': 'John Farmer', 'location': 'Pune', 'role': 'farmer'},
    'admin': {'password': 'admin123', 'name': 'Admin User', 'location': 'Mumbai', 'role': 'admin'},
    'user1': {'password': 'pass123', 'name': 'User One', 'location': 'Delhi', 'role': 'farmer'},
    'user2': {'password': 'pass456', 'name': 'User Two', 'location': 'Bangalore', 'role': 'farmer'}
}

def token_required(f):
    def decorated(*args, **kwargs):
        if app.config['DISABLE_AUTH']:
            return f('dev_user', *args, **kwargs)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Missing or invalid token'}), 401
        token = auth_header.split(' ')[1]
        if token != 'mock-valid-token':
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        return f('authenticated_user', *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    """Dynamic login endpoint for multiple users"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No login data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

        if username in mock_users and mock_users[username]['password'] == password:
            user_data = mock_users[username]
            user_info = {
                'user_id': username,
                'name': user_data['name'],
                'location': user_data['location'],
                'role': user_data['role'],
                'profilePic': f'https://api.dicebear.com/7.x/avataaars/svg?seed={username}',
                'since': '2023',
                'phone': f'+91{9876543210 + hash(username) % 1000000000}',
                'acres': 25 + hash(username) % 50  
            }

            token = 'mock-valid-token'

            return jsonify({
                'status': 'success',
                'message': f'Welcome back, {user_data["name"]}!',
                'token': token,
                'user': user_info
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'status': 'error', 'message': 'Login failed'}), 500

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api')
def api_home():
    return jsonify({
        'message': ' Agriculture AI API Server - Fertilizer & Crop Recommendation',
        'status': 'success',
        'version': '2.0',
        'endpoints': {
            'fertilizer': '/api/fertilizer/recommend',
            'crop': '/api/crop/recommend',
            'soil_analysis': '/api/soil/analyze',
            'weather_current': '/api/weather/current',
            'weather_forecast': '/api/weather/forecast',
            'agricultural_advice': '/api/weather/agricultural-advice',
            'config': '/api/config/features',
            'health': '/api/health'
        }
    })

@app.route('/api/fertilizer/recommend', methods=['POST'])
@token_required
def recommend_fertilizer(current_user):
    """Main fertilizer recommendation endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data received. Please provide soil and crop information.'
            }), 400

        result = my_predictor.predict_fertilizer(data)

        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Fertilizer recommendation generated successfully',
                'data': {
                    'recommended_fertilizer': result['fertilizer'],
                    'confidence_score': result['confidence'],
                    'recommendation_message': result['recommendation'],
                    'nutrient_analysis': result['nutrient_analysis'],
                    'soil_analysis': result['soil_info']
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 400

    except Exception as e:
        logger.error(f"Fertilizer recommendation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/crop/recommend', methods=['POST'])
@token_required
def recommend_crop(current_user):
    """Crop recommendation endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        result = my_predictor.predict_crop(data)

        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Crop recommendation generated successfully',
                'data': {
                    'recommended_crop': result['crop'],
                    'input_conditions': result['conditions']
                }
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 400

    except Exception as e:
        logger.error(f"Crop recommendation error: {e}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/soil/analyze', methods=['POST'])
@token_required
def analyze_soil_endpoint(current_user):
    """Soil analysis endpoint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received. Please provide soil parameters.'}), 400

        result = my_predictor.analyze_soil(data)

        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Soil analysis completed successfully',
                'data': {
                    'soil_health_score': result['soil_health_score'],
                    'fertility_level': result['fertility_level'],
                    'nutrients': result['nutrients'],
                    'recommendations': result['recommendations'],
                    'soil_info': result['soil_info']
                }
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 400

    except Exception as e:
        logger.error(f"Soil analysis error: {e}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/config/features', methods=['GET'])
def get_feature_config():
    """Get all feature configurations for frontend"""
    return jsonify({
        'status': 'success',
        'data': {
            'fertilizer': datasets_info['fertilizer'],
            'crop': datasets_info['crop']
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    models_loaded = len(my_predictor.models) > 0
    return jsonify({
        'status': 'healthy' if models_loaded else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': models_loaded,
        'available_models': list(my_predictor.models.keys()),
        'server': 'Agriculture AI API'
    })

@app.route('/api/weather', methods=['POST'])
@token_required
def get_weather(current_user):
    """Get comprehensive weather data for a location"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received. Please provide location.'}), 400

        location = data.get('location', 'Pune').strip()
        if not location:
            return jsonify({'status': 'error', 'message': 'Location parameter is required'}), 400

        
        current_weather = get_weather_data(location)
        forecast = get_weather_forecast(location, days=5)
        agricultural_advice = get_agricultural_advice(location)

        return jsonify({
            'status': 'success',
            'message': f'Weather data for {location}',
            'data': {
                'current_weather': current_weather,
                'forecast': forecast.get('forecast', []),
                'agricultural_advice': agricultural_advice.get('recommendations', [])
            }
        }), 200

    except Exception as e:
        logger.error(f"Weather data error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to fetch weather data: {str(e)}'}), 500

@app.route('/api/weather/current', methods=['GET'])
@token_required
def get_current_weather(current_user):
    """Get current weather data for a location"""
    try:
        location = request.args.get('location', 'Pune').strip()
        if not location:
            return jsonify({'status': 'error', 'message': 'Location parameter is required'}), 400

        weather_data = get_weather_data(location)
        return jsonify({
            'status': 'success',
            'message': f'Current weather data for {location}',
            'data': weather_data
        }), 200

    except Exception as e:
        logger.error(f"Weather data error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to fetch weather data: {str(e)}'}), 500

@app.route('/api/weather/forecast', methods=['GET'])
@token_required
def get_weather_forecast_endpoint(current_user):
    """Get weather forecast for a location"""
    try:
        location = request.args.get('location', 'Pune').strip()
        days = int(request.args.get('days', 5))
        days = max(1, min(days, 7))  

        if not location:
            return jsonify({'status': 'error', 'message': 'Location parameter is required'}), 400

        forecast_data = get_weather_forecast(location, days)
        return jsonify({
            'status': 'success',
            'message': f'{days}-day weather forecast for {location}',
            'data': forecast_data
        }), 200

    except Exception as e:
        logger.error(f"Weather forecast error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to fetch weather forecast: {str(e)}'}), 500

@app.route('/api/weather/agricultural-advice', methods=['GET'])
@token_required
def get_agricultural_advice_endpoint(current_user):
    """Get agricultural advice based on weather conditions"""
    try:
        location = request.args.get('location', 'Pune').strip()
        current_crop = request.args.get('crop', '').strip()

        if not location:
            return jsonify({'status': 'error', 'message': 'Location parameter is required'}), 400

        advice_data = get_agricultural_advice(location, current_crop if current_crop else None)
        return jsonify({
            'status': 'success',
            'message': f'Agricultural advice for {location}',
            'data': advice_data
        }), 200

    except Exception as e:
        logger.error(f"Agricultural advice error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to generate agricultural advice: {str(e)}'}), 500

@app.route('/dev/fertilizer', methods=['POST'])
def dev_fertilizer():
    """Development fertilizer endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        result = my_predictor.predict_fertilizer(data)
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Fertilizer recommendation generated successfully',
                'data': {
                    'recommended_fertilizer': result['fertilizer'],
                    'confidence_score': result['confidence'],
                    'recommendation_message': result['recommendation'],
                    'nutrient_analysis': result['nutrient_analysis'],
                    'soil_analysis': result['soil_info']
                }
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/dev/crop', methods=['POST'])
def dev_crop():
    """Development crop endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        result = my_predictor.predict_crop(data)
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Crop recommendation generated successfully',
                'data': {
                    'recommended_crop': result['crop'],
                    'input_conditions': result['conditions']
                }
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/dev/soil', methods=['POST'])
def dev_soil():
    """Development soil analysis endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        result = my_predictor.analyze_soil(data)
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Soil analysis completed successfully',
                'data': {
                    'soil_health_score': result['soil_health_score'],
                    'fertility_level': result['fertility_level'],
                    'nutrients': result['nutrients'],
                    'recommendations': result['recommendations'],
                    'soil_info': result['soil_info']
                }
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['error']}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405

if __name__ == '__main__':
    print('Starting Agriculture AI API Server...')
    print(' Fertilizer & Crop Recommendation System')
    print('=' * 50)
    print(' Models Status:', 'Loaded' if my_predictor.models else 'Not Loaded')
    print(' Available Models:', list(my_predictor.models.keys()))
    print(' Server running on: http://localhost:5000')
    print(' Debug mode:', app.config['DEBUG'])
    print(' Authentication:', 'Disabled' if app.config['DISABLE_AUTH'] else 'Enabled')
    print('=' * 50)

    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])