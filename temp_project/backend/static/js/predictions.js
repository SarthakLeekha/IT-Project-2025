
class Predictions {
    constructor() {
        this.predictionCount = 0;
    }

    async init() {
        this.loadPredictionHistory();
    }

    async handleSoilAnalysis(event) {
        if (event) event.preventDefault();

        const form = document.getElementById('soil-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        Object.keys(data).forEach(key => {
            data[key] = parseFloat(data[key]);
        });

        const requiredFields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
        const errors = Utils.validateForm(data, requiredFields);

        if (errors.length > 0) {
            Utils.showNotification(errors.join(', '), 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = Utils.showLoading(submitBtn, 'Analyzing...');

        try {
            const result = await API.analyzeSoil(data);

            if (result.success) {
                this.displaySoilResults(result.data);
                this.updatePredictionCount();
                Utils.showNotification('Soil analysis completed!', 'success');
            } else {
                Utils.showNotification(result.error || 'Soil analysis failed', 'error');
            }
        } catch (error) {
            console.error('Soil analysis error:', error);
            Utils.showNotification('Failed to analyze soil. Please try again.', 'error');
        } finally {
            Utils.hideLoading(submitBtn, originalText);
        }
    }

    async handleCropRecommendation(event) {
        if (event) event.preventDefault();

        const form = document.getElementById('crop-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        Object.keys(data).forEach(key => {
            data[key] = parseFloat(data[key]);
        });

        const requiredFields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
        const errors = Utils.validateForm(data, requiredFields);

        if (errors.length > 0) {
            Utils.showNotification(errors.join(', '), 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = Utils.showLoading(submitBtn, 'Analyzing...');

        try {
            const result = await API.predictCrop(data);

            if (result.success) {
                this.displayCropResults(result.data);
                this.updatePredictionCount();
                Utils.showNotification('Crop recommendation generated!', 'success');
            } else {
                Utils.showNotification(result.error || 'Crop recommendation failed', 'error');
            }
        } catch (error) {
            console.error('Crop recommendation error:', error);
            Utils.showNotification('Failed to recommend crops. Please try again.', 'error');
        } finally {
            Utils.hideLoading(submitBtn, originalText);
        }
    }

    async handleFertilizerRecommendation(event) {
        if (event) event.preventDefault();

        const form = document.getElementById('fertilizer-form');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        const numericFields = ['Temparature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous'];
        numericFields.forEach(field => {
            if (data[field]) {
                data[field] = parseFloat(data[field]);
            }
        });

        const requiredFields = ['Soil Type', 'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous'];
        const errors = Utils.validateForm(data, requiredFields);

        if (errors.length > 0) {
            Utils.showNotification(errors.join(', '), 'error');
            return;
        }

        const backendData = {
            crop_type: data['Crop Type'],
            soil_type: data['Soil Type'],
            nitrogen: data['Nitrogen'],
            phosphorus: data['Phosphorous'],
            potassium: data['Potassium'],
            soil_ph: 6.5
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = Utils.showLoading(submitBtn, 'Analyzing...');

        try {
            const result = await API.predictFertilizer(backendData);

            if (result.success) {
                this.displayFertilizerResults(result.data);
                this.updatePredictionCount();
                Utils.showNotification('Fertilizer recommendation generated!', 'success');
            } else {
                Utils.showNotification(result.error || 'Fertilizer recommendation failed', 'error');
            }
        } catch (error) {
            console.error('Fertilizer recommendation error:', error);
            Utils.showNotification('Failed to recommend fertilizer. Please try again.', 'error');
        } finally {
            Utils.hideLoading(submitBtn, originalText);
        }
    }

    displaySoilResults(data) {
        const resultsContainer = document.getElementById('soil-results');
        const resultContent = document.getElementById('soil-result-content');

        if (!resultsContainer || !resultContent) return;

        const healthScore = data.soil_health_score || 0;
        const fertilityLevel = data.fertility_level || 'Unknown';
        const recommendations = data.recommendations || [];

        resultContent.innerHTML = `
            <div class="result-card bg-green-50 p-4 rounded-xl border border-green-200 mb-4">
                <div class="flex items-center justify-between mb-2">
                    <h5 class="font-bold text-green-800">Soil Health Score</h5>
                    <span class="text-2xl font-bold text-green-700">${healthScore}/100</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
                    <div class="bg-green-500 h-3 rounded-full transition-all duration-1000" style="width: ${healthScore}%"></div>
                </div>
                <p class="text-sm text-green-700">Fertility Level: <span class="font-semibold">${fertilityLevel}</span></p>
            </div>

            ${data.nutrients ? `
            <div class="grid grid-cols-3 gap-3 mb-4">
                <div class="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <div class="text-sm font-medium text-blue-800">Nitrogen (N)</div>
                    <div class="text-lg font-bold text-blue-700">${data.nutrients.N?.value || 'N/A'}</div>
                    <div class="text-xs text-blue-600">${Utils.capitalizeFirst(data.nutrients.N?.level || 'unknown')}</div>
                </div>
                <div class="bg-purple-50 p-3 rounded-lg border border-purple-200">
                    <div class="text-sm font-medium text-purple-800">Phosphorus (P)</div>
                    <div class="text-lg font-bold text-purple-700">${data.nutrients.P?.value || 'N/A'}</div>
                    <div class="text-xs text-purple-600">${Utils.capitalizeFirst(data.nutrients.P?.level || 'unknown')}</div>
                </div>
                <div class="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                    <div class="text-sm font-medium text-yellow-800">Potassium (K)</div>
                    <div class="text-lg font-bold text-yellow-700">${data.nutrients.K?.value || 'N/A'}</div>
                    <div class="text-xs text-yellow-600">${Utils.capitalizeFirst(data.nutrients.K?.level || 'unknown')}</div>
                </div>
            </div>
            ` : ''}

            <div class="bg-gray-50 p-4 rounded-xl border border-gray-200">
                <h6 class="font-semibold text-gray-800 mb-2">Recommendations</h6>
                <ul class="text-sm text-gray-700 space-y-1">
                    ${recommendations.map(rec => `<li class="flex items-start"><span class="text-green-500 mr-2"></span>${rec}</li>`).join('')}
                </ul>
            </div>
        `;

        resultsContainer.classList.remove('hidden');
    }

    displayCropResults(data) {
        const resultsContainer = document.getElementById('crop-results');
        const resultContent = document.getElementById('crop-result-content');

        if (!resultsContainer || !resultContent) return;

        const crop = data.recommended_crop || 'Unknown';
        const conditions = data.input_conditions || {};

        resultContent.innerHTML = `
            <div class="result-card bg-amber-50 p-4 rounded-xl border border-amber-200 mb-4">
                <div class="flex items-center justify-between mb-2">
                    <h5 class="font-bold text-amber-800">Recommended Crop</h5>
                    <span class="text-xl font-bold text-amber-700">${Utils.capitalizeFirst(crop)}</span>
                </div>
                <div class="grid grid-cols-2 gap-3 text-sm">
                    <div>N: <span class="font-semibold">${conditions.N || 'N/A'}</span></div>
                    <div>P: <span class="font-semibold">${conditions.P || 'N/A'}</span></div>
                    <div>K: <span class="font-semibold">${conditions.K || 'N/A'}</span></div>
                    <div>pH: <span class="font-semibold">${conditions.ph || 'N/A'}</span></div>
                    <div>Temperature: <span class="font-semibold">${conditions.temperature || 'N/A'}C</span></div>
                    <div>Rainfall: <span class="font-semibold">${conditions.rainfall || 'N/A'}mm</span></div>
                </div>
            </div>
        `;

        resultsContainer.classList.remove('hidden');
    }

    displayFertilizerResults(data) {
        const resultsContainer = document.getElementById('fertilizer-results');
        const resultContent = document.getElementById('fertilizer-result-content');

        if (!resultsContainer || !resultContent) return;

        const fertilizer = data.recommended_fertilizer || 'Unknown';
        const confidence = data.confidence_score ? (data.confidence_score * 100).toFixed(1) : 'N/A';
        const recommendation = data.recommendation_message || '';

        resultContent.innerHTML = `
            <div class="result-card bg-blue-50 p-4 rounded-xl border border-blue-200 mb-4">
                <div class="flex items-center justify-between mb-2">
                    <h5 class="font-bold text-blue-800">Recommended Fertilizer</h5>
                    <span class="text-xl font-bold text-blue-700">${fertilizer}</span>
                </div>
                ${confidence !== 'N/A' ? `
                <div class="mb-2">
                    <div class="flex justify-between text-sm mb-1">
                        <span>Confidence</span>
                        <span>${confidence}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-500 h-2 rounded-full transition-all duration-1000" style="width: ${confidence}%"></div>
                    </div>
                </div>
                ` : ''}
                <p class="text-sm text-blue-700">${recommendation}</p>
            </div>

            ${data.nutrient_analysis ? `
            <div class="grid grid-cols-3 gap-3 mb-4">
                <div class="bg-red-50 p-3 rounded-lg border border-red-200">
                    <div class="text-sm font-medium text-red-800">Nitrogen</div>
                    <div class="text-lg font-bold text-red-700">${data.nutrient_analysis.nitrogen?.value || 'N/A'}</div>
                    <div class="text-xs text-red-600">${Utils.capitalizeFirst(data.nutrient_analysis.nitrogen?.level || 'unknown')}</div>
                </div>
                <div class="bg-orange-50 p-3 rounded-lg border border-orange-200">
                    <div class="text-sm font-medium text-orange-800">Phosphorus</div>
                    <div class="text-lg font-bold text-orange-700">${data.nutrient_analysis.phosphorus?.value || 'N/A'}</div>
                    <div class="text-xs text-orange-600">${Utils.capitalizeFirst(data.nutrient_analysis.phosphorus?.level || 'unknown')}</div>
                </div>
                <div class="bg-indigo-50 p-3 rounded-lg border border-indigo-200">
                    <div class="text-sm font-medium text-indigo-800">Potassium</div>
                    <div class="text-lg font-bold text-indigo-700">${data.nutrient_analysis.potassium?.value || 'N/A'}</div>
                    <div class="text-xs text-indigo-600">${Utils.capitalizeFirst(data.nutrient_analysis.potassium?.level || 'unknown')}</div>
                </div>
            </div>
            ` : ''}
        `;

        resultsContainer.classList.remove('hidden');
    }

    updatePredictionCount() {
        this.predictionCount++;
        const counterElement = document.getElementById('total-predictions');
        if (counterElement) {
            Utils.animateCounter(counterElement, this.predictionCount);
        }
        this.savePredictionHistory();
    }

    savePredictionHistory() {
        const history = Utils.getFromLocalStorage('predictionHistory') || [];
        history.push({
            timestamp: new Date().toISOString(),
            count: this.predictionCount
        });

        if (history.length > 100) {
            history.shift();
        }

        Utils.saveToLocalStorage('predictionHistory', history);
    }

    loadPredictionHistory() {
        const history = Utils.getFromLocalStorage('predictionHistory') || [];
        if (history.length > 0) {
            this.predictionCount = history[history.length - 1].count || 0;
            const counterElement = document.getElementById('total-predictions');
            if (counterElement) {
                counterElement.textContent = this.predictionCount;
            }
        }
    }
}


window.Predictions = new Predictions();


document.addEventListener('DOMContentLoaded', () => {
    if (window.Predictions) {
        window.Predictions.init();
        
        
        const soilForm = document.getElementById('soil-form');
        const cropForm = document.getElementById('crop-form');
        const fertilizerForm = document.getElementById('fertilizer-form');

        if (soilForm) {
            soilForm.addEventListener('submit', (e) => window.Predictions.handleSoilAnalysis(e));
        }
        if (cropForm) {
            cropForm.addEventListener('submit', (e) => window.Predictions.handleCropRecommendation(e));
        }
        if (fertilizerForm) {
            fertilizerForm.addEventListener('submit', (e) => window.Predictions.handleFertilizerRecommendation(e));
        }
    }
});