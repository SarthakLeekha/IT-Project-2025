
class Utils {
    static showNotification(message, type = 'success', duration = 5000) {
       t
        let notification = document.getElementById('notification');
        let notificationText = document.getElementById('notification-text');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'notification';
            notification.innerHTML = `
                <i class="fas fa-check-circle mr-3 text-lg"></i>
                <span id="notification-text">${message}</span>
            `;
            document.body.appendChild(notification);
            notificationText = document.getElementById('notification-text');
        }

        notificationText.textContent = message;
        notification.className = `notification ${type}`;

        const icon = notification.querySelector('i');
        if (type === 'success') {
            icon.className = 'fas fa-check-circle mr-3 text-lg';
        } else if (type === 'error') {
            icon.className = 'fas fa-exclamation-circle mr-3 text-lg';
        } else if (type === 'warning') {
            icon.className = 'fas fa-exclamation-triangle mr-3 text-lg';
        }

        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, duration);
    }

    static showLoading(button, text = 'Processing...') {
        if (!button) return '';
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `${text} <div class="loading-spinner ml-2"></div>`;
        return originalText;
    }

    static hideLoading(button, originalText) {
        if (!button) return;
        button.disabled = false;
        button.innerHTML = originalText;
    }

    static validateForm(formData, requiredFields) {
        const errors = [];
        
        requiredFields.forEach(field => {
            if (!formData[field] || formData[field].toString().trim() === '') {
                errors.push(`${field.charAt(0).toUpperCase() + field.slice(1)} is required`);
            }
        });

        return errors;
    }

    static capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    static formatNumber(num, decimals = 2) {
        return Number(num).toFixed(decimals);
    }

    static saveToLocalStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    }

    static getFromLocalStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return null;
        }
    }

    static clearLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    }

    static animateCounter(element, target, duration = 1000) {
        if (!element) return;
        
        const start = parseInt(element.textContent) || 0;
        const increment = (target - start) / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    static sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

   
    static async mockApiCall(endpoint, data = null) {
        await Utils.sleep(1000); 
        
        
        switch(endpoint) {
            case '/api/health':
                return {
                    status: 'success',
                    available_models: ['crop_recommendation', 'fertilizer_prediction', 'soil_analysis'],
                    message: 'Backend is running'
                };
            
            case '/api/fertilizer':
                return {
                    status: 'success',
                    data: {
                        recommended_fertilizer: 'Urea',
                        confidence_score: 0.85,
                        recommendation_message: 'Apply Urea for nitrogen deficiency. Best for vegetative growth.',
                        nutrient_analysis: {
                            nitrogen: { value: data?.nitrogen || 10, level: 'low', deficient: 1 },
                            phosphorus: { value: data?.phosphorus || 10, level: 'low', deficient: 1 },
                            potassium: { value: data?.potassium || 10, level: 'low', deficient: 1 }
                        },
                        soil_analysis: {
                            ph: data?.soil_ph || 6.5,
                            status: 'optimal',
                            type: data?.soil_type || 'loamy'
                        }
                    },
                    message: 'Fertilizer recommendation generated successfully'
                };
            
            case '/api/crop':
                return {
                    status: 'success',
                    data: {
                        recommended_crop: 'wheat',
                        input_conditions: data || {}
                    },
                    message: 'Crop recommendation generated successfully'
                };
            
            case '/api/soil':
                return {
                    status: 'success',
                    data: {
                        soil_health_score: 75,
                        fertility_level: 'Medium',
                        nutrients: {
                            N: { value: data?.N || 72, level: 'medium', percentage: 48 },
                            P: { value: data?.P || 42, level: 'medium', percentage: 28 },
                            K: { value: data?.K || 58, level: 'medium', percentage: 38.7 }
                        },
                        recommendations: [
                            'Add compost to improve organic matter',
                            'Maintain current watering schedule',
                            'Test soil again in 3 months'
                        ],
                        soil_info: {
                            moisture: 25,
                            organic_carbon: 1.5,
                            ph: data?.ph || 6.5,
                            ph_status: 'optimal',
                            type: 'loamy'
                        }
                    },
                    message: 'Soil analysis completed successfully'
                };
            
            default:
                return {
                    status: 'error',
                    message: 'Endpoint not found'
                };
        }
    }
}


window.Utils = Utils;