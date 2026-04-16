class API {
    constructor() {
        this.baseURL = 'https://it-project-2025-vkfb.onrender.com';
        this.timeout = 10000;
        this.useMockData = false;
    }

    async makeRequest(endpoint, options = {}) {
        if (!endpoint.startsWith('/')) {
            endpoint = '/' + endpoint;
        }

        const url = this.baseURL + endpoint;

        if (this.useMockData) {
            return Utils.mockApiCall(endpoint, options.body);
        }

        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (config.method !== 'GET' && options.body) {
            config.body = JSON.stringify(options.body);
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            config.signal = controller.signal;

            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            this.useMockData = true;
            return Utils.mockApiCall(endpoint, options.body);
        }
    }

    async checkBackendConnection() {
        try {
            const response = await this.makeRequest('/api/health');
            return {
                connected: true,
                status: response.status,
                models: response.available_models || []
            };
        } catch (error) {
            return {
                connected: false,
                message: 'Using demo mode'
            };
        }
    }

    async predictCrop(data) {
        return await this.makeRequest('/api/crop', {
            method: 'POST',
            body: data
        });
    }

    async predictFertilizer(data) {
        return await this.makeRequest('/api/fertilizer', {
            method: 'POST',
            body: data
        });
    }

    async analyzeSoil(data) {
        return await this.makeRequest('/api/soil', {
            method: 'POST',
            body: data
        });
    }

    async getCurrentWeather(location = 'Pune') {
        return await this.makeRequest(`/api/weather?location=${encodeURIComponent(location)}`);
    }
}

window.API = new API();
