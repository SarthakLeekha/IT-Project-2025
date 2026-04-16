class Utils {
    static showNotification(message, type = 'success', duration = 5000) {
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

    static saveToLocalStorage(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    }

    static getFromLocalStorage(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
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
                    available_models: ['crop_recommendation', 'fertilizer_prediction', 'soil_analysis']
                };
            default:
                return { status: 'error' };
        }
    }
}

window.Utils = Utils;
