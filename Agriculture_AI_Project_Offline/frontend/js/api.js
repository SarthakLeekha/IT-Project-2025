class API {
    constructor() {

        this.baseURL = 'http://backend:5000';
        this.timeout = 10000;
        this.useMockData = false; // Start in demo mode by default
    }

    async makeRequest(endpoint, options = {}) {

        if (this.useMockData) {
            console.log('Using mock data for:', endpoint);
            return Utils.mockApiCall(endpoint, options.body);
        }

        const url = `${this.baseURL}${endpoint}`;
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

            console.log(' Making API request to:', url);
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('API response:', data);
            return data;

        } catch (error) {
            console.error(' API Request failed:', error);


            if (error.name === 'AbortError') {
                console.log(' Request timeout, using mock data');
                this.useMockData = true;
                return Utils.mockApiCall(endpoint, options.body);
            } else if (error.message.includes('Failed to fetch')) {
                console.log('Backend not available, using mock data');
                this.useMockData = true;
                return Utils.mockApiCall(endpoint, options.body);
            }

            throw error;
        }
    }

    async checkBackendConnection() {
        try {
            const response = await this.makeRequest('/api/health');
            return {
                connected: true,
                models: response.available_models || [],
                status: response.status,
                message: 'Backend connected successfully'
            };
        } catch (error) {
            console.error('Backend connection check failed:', error);
            return {
                connected: false,
                error: error.message,
                message: 'Using demo mode with mock data'
            };
        }
    }

    async login(credentials) {
        try {
            await Utils.sleep(1000);


            const demoUsers = {
                'farmer': { username: 'farmer', password: 'agrio123', name: 'John Farmer', role: 'farmer' },
                'admin': { username: 'admin', password: 'admin123', name: 'Admin User', role: 'admin' },
                'user1': { username: 'user1', password: 'pass123', name: 'Test User', role: 'user' }
            };

            const user = demoUsers[credentials.username];
            if (user && user.password === credentials.password) {
                const userData = {
                    username: user.username,
                    name: user.name,
                    role: user.role,
                    loginTime: new Date().toISOString()
                };

                Utils.saveToLocalStorage('user', userData);
                Utils.saveToLocalStorage('token', 'demo-token-' + Date.now());

                return {
                    success: true,
                    user: userData,
                    token: 'demo-token-' + Date.now(),
                    message: 'Login successful'
                };
            } else {
                return {
                    success: false,
                    error: 'Invalid username or password'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async logout() {
        try {
            Utils.clearLocalStorage('user');
            Utils.clearLocalStorage('token');
            return { success: true };
        } catch (error) {
            console.error('Logout error:', error);
            return { success: false, error: error.message };
        }
    }

    async getCurrentUser() {
        const user = Utils.getFromLocalStorage('user');
        const token = Utils.getFromLocalStorage('token');
        return user && token ? { user, token } : null;
    }


    async predictFertilizer(data) {
        try {
            const response = await this.makeRequest('/api/fertilizer', {
                method: 'POST',
                body: data
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Fertilizer prediction failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async predictCrop(data) {
        try {
            const response = await this.makeRequest('/api/crop', {
                method: 'POST',
                body: data
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Crop prediction failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async analyzeSoil(data) {
        try {
            const response = await this.makeRequest('/api/soil', {
                method: 'POST',
                body: data
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Soil analysis failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getCurrentWeather(location = 'Pune') {
        try {
            const response = await this.makeRequest(`/api/weather?location=${encodeURIComponent(location)}`);

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Weather data fetch failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getWeatherForecast(location = 'Pune', days = 5) {
        try {
            const response = await this.makeRequest(`/api/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`);

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Weather forecast fetch failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getAgriculturalAdvice(location = 'Pune', crop = '') {
        try {
            let url = `/api/weather/agricultural-advice?location=${encodeURIComponent(location)}`;
            if (crop) {
                url += `&crop=${encodeURIComponent(crop)}`;
            }

            const response = await this.makeRequest(url);

            if (response.status === 'success') {
                return {
                    success: true,
                    data: response.data
                };
            } else {
                return {
                    success: false,
                    error: response.message || 'Agricultural advice fetch failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    handleApiError(error, context = '') {
        console.error(`API Error${context ? ` (${context})` : ''}:`, error);

        let message = 'An unexpected error occurred';

        if (error.message.includes('timeout')) {
            message = 'Request timed out. Using demo data instead.';
        } else if (error.message.includes('Failed to fetch')) {
            message = 'Backend not available. Using demo mode.';
        } else if (error.message.includes('HTTP')) {
            message = error.message;
        } else {
            message = error.message;
        }

        Utils.showNotification(message, 'warning');
        return { success: false, error: message };
    }
}


window.API = new API();
