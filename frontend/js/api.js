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

        const token = localStorage.getItem('token');

        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
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

            return await response.json();

        } catch (error) {
            console.error(error);
            this.useMockData = true;
            return Utils.mockApiCall(endpoint, options.body);
        }
    }

    async checkBackendConnection() {
        try {
            const res = await fetch(`${this.baseURL}/api/health`);
            if (!res.ok) throw new Error();
            return { connected: true };
        } catch {
            return { connected: false };
        }
    }

    async login(data) {
        return await this.makeRequest('/api/login', {
            method: 'POST',
            body: data
        });
    }

    async predictCrop(data) {
        return await this.makeRequest('/api/crop/recommend', {
            method: 'POST',
            body: data
        });
    }

    async predictFertilizer(data) {
        return await this.makeRequest('/api/fertilizer/recommend', {
            method: 'POST',
            body: data
        });
    }

    async analyzeSoil(data) {
        return await this.makeRequest('/api/soil/analyze', {
            method: 'POST',
            body: data
        });
    }

    async getCurrentWeather(location = 'Pune') {
        return await this.makeRequest(
            `/api/weather/current?location=${encodeURIComponent(location)}`
        );
    }
}

window.API = new API();
