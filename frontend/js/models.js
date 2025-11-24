
class AgriculturalModels {
    constructor() {
        this.availableModels = {
            CROP_RECOMMENDATION: 'crop_recommendation',
            FERTILIZER_PREDICTION: 'fertilizer_prediction', 
            SOIL_ANALYSIS: 'soil_analysis',
            YIELD_PREDICTION: 'yield_prediction'
        };
        
        this.modelStatus = {};
        this.modelConfig = {};
        this.predictionHistory = [];
        this.init();
    }

    async init() {
        console.log(' Initializing Agricultural Models...');
        await this.loadModelConfig();
        await this.checkModelStatus();
        this.loadPredictionHistory();
        console.log(' Agricultural Models initialized');
    }

    async loadModelConfig() {
        try {
            const savedConfig = Utils.getFromLocalStorage('model_config');
            if (savedConfig) {
                this.modelConfig = savedConfig;
                console.log(' Loaded model config from localStorage');
            } else {
                
                this.modelConfig = {
                    [this.availableModels.CROP_RECOMMENDATION]: {
                        name: 'Crop Recommendation Model',
                        version: '1.2.0',
                        input_features: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
                        output_classes: [
                            'rice', 'wheat', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
                            'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
                            'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
                            'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
                        ],
                        accuracy: 0.94,
                        last_trained: '2024-01-20',
                        description: 'Recommends optimal crops based on soil and climate conditions'
                    },
                    [this.availableModels.FERTILIZER_PREDICTION]: {
                        name: 'Fertilizer Recommendation Model',
                        version: '1.1.0',
                        input_features: ['crop_type', 'soil_type', 'nitrogen', 'phosphorus', 'potassium', 'soil_ph'],
                        output_classes: ['Urea', 'DAP', '14-35-14', '28-28', '17-17-17', '20-20', '10-26-26', 'MOP', 'SSP'],
                        accuracy: 0.89,
                        last_trained: '2024-01-18',
                        description: 'Suggests appropriate fertilizers based on nutrient deficiencies'
                    },
                    [this.availableModels.SOIL_ANALYSIS]: {
                        name: 'Soil Health Analysis Model',
                        version: '1.3.0',
                        input_features: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'],
                        output_features: ['soil_health_score', 'fertility_level', 'nutrient_levels', 'recommendations', 'soil_info'],
                        accuracy: 0.87,
                        last_trained: '2024-01-22',
                        description: 'Analyzes soil health and provides improvement recommendations'
                    },
                    [this.availableModels.YIELD_PREDICTION]: {
                        name: 'Yield Prediction Model',
                        version: '1.0.0',
                        input_features: ['crop_type', 'N', 'P', 'K', 'rainfall', 'temperature'],
                        output_features: ['predicted_yield', 'confidence', 'optimal_conditions'],
                        accuracy: 0.82,
                        last_trained: '2024-01-15',
                        description: 'Predicts crop yield based on environmental factors'
                    }
                };
                Utils.saveToLocalStorage('model_config', this.modelConfig);
                console.log(' Saved default model config to localStorage');
            }
        } catch (error) {
            console.error(' Error loading model config:', error);
        }
    }

    async checkModelStatus() {
        try {
            
            const response = await API.makeRequest('/api/models/status');
            
            if (response.status === 'success') {
                this.modelStatus = response.data;
                console.log(' Model status from backend:', this.modelStatus);
            } else {
                throw new Error('Backend model status unavailable');
            }
        } catch (error) {
            console.warn(' Could not fetch model status from backend, using local fallback');
            
            
            this.modelStatus = {
                [this.availableModels.CROP_RECOMMENDATION]: { 
                    status: 'loaded', 
                    performance: 0.94,
                    last_used: new Date().toISOString(),
                    predictions_today: 12
                },
                [this.availableModels.FERTILIZER_PREDICTION]: { 
                    status: 'loaded', 
                    performance: 0.89,
                    last_used: new Date().toISOString(),
                    predictions_today: 8
                },
                [this.availableModels.SOIL_ANALYSIS]: { 
                    status: 'loaded', 
                    performance: 0.87,
                    last_used: new Date().toISOString(),
                    predictions_today: 15
                },
                [this.availableModels.YIELD_PREDICTION]: { 
                    status: 'available', 
                    performance: 0.82,
                    last_used: new Date().toISOString(),
                    predictions_today: 5
                }
            };
        }
    }

  
    validateInput(inputData, modelType) {
        const errors = [];
        const config = this.modelConfig[modelType];

        if (!config) {
            errors.push('Invalid model type');
            return { valid: false, errors };
        }

       
        config.input_features.forEach(feature => {
            if (inputData[feature] === undefined || inputData[feature] === null || inputData[feature] === '') {
                errors.push(`Missing required feature: ${feature}`);
            }
        });


        if (modelType === this.availableModels.CROP_RECOMMENDATION || 
            modelType === this.availableModels.SOIL_ANALYSIS) {
            
            if (inputData.N !== undefined && (inputData.N < 0 || inputData.N > 140)) {
                errors.push('Nitrogen (N) must be between 0 and 140 ppm');
            }
            if (inputData.P !== undefined && (inputData.P < 5 || inputData.P > 145)) {
                errors.push('Phosphorus (P) must be between 5 and 145 ppm');
            }
            if (inputData.K !== undefined && (inputData.K < 5 || inputData.K > 205)) {
                errors.push('Potassium (K) must be between 5 and 205 ppm');
            }
            if (inputData.temperature !== undefined && (inputData.temperature < -10 || inputData.temperature > 50)) {
                errors.push('Temperature must be between -10 and 50C');
            }
            if (inputData.humidity !== undefined && (inputData.humidity < 0 || inputData.humidity > 100)) {
                errors.push('Humidity must be between 0 and 100%');
            }
            if (inputData.ph !== undefined && (inputData.ph < 3 || inputData.ph > 10)) {
                errors.push('pH must be between 3 and 10');
            }
            if (inputData.rainfall !== undefined && (inputData.rainfall < 0 || inputData.rainfall > 500)) {
                errors.push('Rainfall must be between 0 and 500 mm');
            }
        }

        if (modelType === this.availableModels.FERTILIZER_PREDICTION) {
            if (inputData.nitrogen !== undefined && (inputData.nitrogen < 0 || inputData.nitrogen > 140)) {
                errors.push('Nitrogen must be between 0 and 140 ppm');
            }
            if (inputData.phosphorus !== undefined && (inputData.phosphorus < 5 || inputData.phosphorus > 145)) {
                errors.push('Phosphorus must be between 5 and 145 ppm');
            }
            if (inputData.potassium !== undefined && (inputData.potassium < 5 || inputData.potassium > 205)) {
                errors.push('Potassium must be between 5 and 205 ppm');
            }
            if (inputData.soil_ph !== undefined && (inputData.soil_ph < 3 || inputData.soil_ph > 10)) {
                errors.push('Soil pH must be between 3 and 10');
            }
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }

    
    preprocessCropData(inputData) {
        return {
            N: parseFloat(inputData.N) || 0,
            P: parseFloat(inputData.P) || 0,
            K: parseFloat(inputData.K) || 0,
            temperature: parseFloat(inputData.temperature) || 0,
            humidity: parseFloat(inputData.humidity) || 0,
            ph: parseFloat(inputData.ph) || 0,
            rainfall: parseFloat(inputData.rainfall) || 0
        };
    }

    preprocessFertilizerData(inputData) {
        return {
            crop_type: (inputData.crop_type || '').toLowerCase(),
            soil_type: (inputData.soil_type || '').toLowerCase(),
            nitrogen: parseFloat(inputData.nitrogen) || 0,
            phosphorus: parseFloat(inputData.phosphorus) || 0,
            potassium: parseFloat(inputData.potassium) || 0,
            soil_ph: parseFloat(inputData.soil_ph) || 6.5
        };
    }

    preprocessSoilData(inputData) {
        return {
            N: parseFloat(inputData.N) || 0,
            P: parseFloat(inputData.P) || 0,
            K: parseFloat(inputData.K) || 0,
            temperature: parseFloat(inputData.temperature) || 0,
            humidity: parseFloat(inputData.humidity) || 0,
            ph: parseFloat(inputData.ph) || 0,
            rainfall: parseFloat(inputData.rainfall) || 0
        };
    }

    
    getModelInfo(modelType) {
        return this.modelConfig[modelType] || null;
    }

    getModelStatus(modelType) {
        return this.modelStatus[modelType] || { status: 'unknown', performance: 0 };
    }

    getAllModels() {
        return this.modelConfig;
    }

    getAvailableModels() {
        return Object.values(this.availableModels);
    }

   
    logPrediction(modelType, input, output, success = true) {
        const predictionLog = {
            id: Utils.generateId ? Utils.generateId() : Date.now().toString(),
            timestamp: new Date().toISOString(),
            model_type: modelType,
            input: input,
            output: output,
            success: success,
            processing_time: Math.random() * 500 + 100 
        };

        this.predictionHistory.push(predictionLog);
        
        
        if (this.modelStatus[modelType]) {
            this.modelStatus[modelType].last_used = predictionLog.timestamp;
            this.modelStatus[modelType].predictions_today = 
                (this.modelStatus[modelType].predictions_today || 0) + 1;
        }

       
        this.savePredictionHistory();

        return predictionLog;
    }

    savePredictionHistory() {
        try {
            
            if (this.predictionHistory.length > 1000) {
                this.predictionHistory = this.predictionHistory.slice(-1000);
            }
            Utils.saveToLocalStorage('model_prediction_history', this.predictionHistory);
        } catch (error) {
            console.error('Error saving prediction history:', error);
        }
    }

    loadPredictionHistory() {
        try {
            const history = Utils.getFromLocalStorage('model_prediction_history');
            if (history && Array.isArray(history)) {
                this.predictionHistory = history;
            }
        } catch (error) {
            console.error('Error loading prediction history:', error);
        }
    }

    getPredictionStats() {
        const stats = {
            total_predictions: this.predictionHistory.length,
            successful_predictions: this.predictionHistory.filter(log => log.success).length,
            failed_predictions: this.predictionHistory.filter(log => !log.success).length,
            model_usage: {},
            average_processing_time: 0
        };

        
        this.predictionHistory.forEach(log => {
            if (!stats.model_usage[log.model_type]) {
                stats.model_usage[log.model_type] = 0;
            }
            stats.model_usage[log.model_type]++;
        });

      
        if (this.predictionHistory.length > 0) {
            const totalTime = this.predictionHistory.reduce((sum, log) => sum + log.processing_time, 0);
            stats.average_processing_time = totalTime / this.predictionHistory.length;
        }

        return stats;
    }

    getRecentPredictions(limit = 10) {
        return this.predictionHistory
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, limit);
    }

    
    async performHealthCheck() {
        const healthReport = {
            timestamp: new Date().toISOString(),
            overall_status: 'healthy',
            models: {},
            issues: []
        };

        for (const [modelType, config] of Object.entries(this.modelConfig)) {
            const status = this.getModelStatus(modelType);
            healthReport.models[modelType] = {
                name: config.name,
                status: status.status,
                performance: status.performance,
                last_used: status.last_used,
                predictions_today: status.predictions_today || 0
            };

            if (status.status !== 'loaded' && status.status !== 'available') {
                healthReport.issues.push(`Model ${config.name} is not available`);
                healthReport.overall_status = 'degraded';
            }

            if (status.performance < 0.8) {
                healthReport.issues.push(`Model ${config.name} has low performance: ${(status.performance * 100).toFixed(1)}%`);
                healthReport.overall_status = 'degraded';
            }
        }

        return healthReport;
    }

   
    getModelDisplayName(modelType) {
        const config = this.modelConfig[modelType];
        return config ? config.name : modelType;
    }

    getModelDescription(modelType) {
        const config = this.modelConfig[modelType];
        return config ? config.description : 'No description available';
    }

    formatModelOutput(modelType, output) {
        switch (modelType) {
            case this.availableModels.CROP_RECOMMENDATION:
                return {
                    type: 'crop',
                    value: output.recommended_crop,
                    confidence: output.confidence || 0.85,
                    alternatives: this.getAlternativeCrops(output.recommended_crop)
                };
            
            case this.availableModels.FERTILIZER_PREDICTION:
                return {
                    type: 'fertilizer',
                    value: output.recommended_fertilizer,
                    confidence: output.confidence_score || 0.80,
                    analysis: output.nutrient_analysis,
                    recommendation: output.recommendation_message
                };
            
            case this.availableModels.SOIL_ANALYSIS:
                return {
                    type: 'soil',
                    health_score: output.soil_health_score,
                    fertility_level: output.fertility_level,
                    nutrients: output.nutrients,
                    recommendations: output.recommendations
                };
            
            default:
                return output;
        }
    }

    getAlternativeCrops(primaryCrop) {
        const alternatives = {
            'rice': ['wheat', 'maize', 'barley'],
            'wheat': ['barley', 'oats', 'rye'],
            'maize': ['sorghum', 'millet', 'soybean'],
            'cotton': ['jute', 'hemp', 'flax'],
            'sugarcane': ['sugar beet', 'sweet sorghum']
        };
        
        return alternatives[primaryCrop] || ['wheat', 'maize', 'barley'];
    }

   
    async simulateRetraining(modelType) {
        console.log(` Simulating retraining for ${modelType}`);
        
      
        await Utils.sleep(2000);
        
       
        if (this.modelStatus[modelType]) {
            const currentPerf = this.modelStatus[modelType].performance;
            const improvement = (Math.random() * 0.05) - 0.02; // -2% to +3% change
            this.modelStatus[modelType].performance = Math.max(0.7, Math.min(0.99, currentPerf + improvement));
            this.modelStatus[modelType].last_trained = new Date().toISOString();
        }
        
        return {
            success: true,
            message: `Model ${modelType} retraining simulated successfully`,
            new_performance: this.modelStatus[modelType]?.performance
        };
    }
}


window.AgriculturalModels = new AgriculturalModels();


document.addEventListener('DOMContentLoaded', () => {
    if (window.AgriculturalModels) {
        window.AgriculturalModels.init().then(() => {
            console.log(' Agricultural Models ready for predictions');
        }).catch(error => {
            console.error(' Failed to initialize Agricultural Models:', error);
        });
    }
});