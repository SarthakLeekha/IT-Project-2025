
class App {
    constructor() {
        this.initialized = false;
        this.charts = {};
    }

    async init() {
        try {
            console.log('Initializing Agrio Platform...');

           
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeApp());
            } else {
                await this.initializeApp();
            }
        } catch (error) {
            console.error('Failed to initialize app:', error);
            Utils.showNotification('Failed to initialize application', 'error');
        }
    }

    async initializeApp() {
        try {
            console.log('Starting app initialization...');
            
            
            if (window.Auth) {
                await window.Auth.init();
            }
            
         
            await this.checkBackendConnection();

            
            this.setupEventListeners();

            this.initializeCharts();

            this.initialized = true;
            console.log('Agrio Platform initialized successfully');

        } catch (error) {
            console.error('App initialization error:', error);
            Utils.showNotification('Application initialized with demo data', 'warning');
        }
    }

    async checkBackendConnection() {
        console.log('Checking backend connection...');

        const connectionDetails = document.getElementById('connection-details');
        if (!connectionDetails) {
            console.log('Connection details element not found');
            return;
        }

        try {
            const connectionResult = await API.checkBackendConnection();

            if (connectionResult.connected) {
                console.log('Backend connected:', connectionResult.models);

                connectionDetails.innerHTML = `
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-green-500 rounded-full mr-2 pulse-dot"></div>
                        <span>Connected to backend</span>
                    </div>
                    <div class="text-green-600 text-xs mt-1">
                        Models: ${connectionResult.models.join(', ')}
                    </div>
                `;

                const modelStatus = document.getElementById('model-status');
                if (modelStatus) {
                    modelStatus.textContent = 'AI Active';
                }

            } else {
                console.warn('Backend connection failed:', connectionResult.error);

                connectionDetails.innerHTML = `
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                        <span>Demo Mode - Backend Offline</span>
                    </div>
                    <div class="text-yellow-600 text-xs mt-1">
                        ${connectionResult.message || 'Using demo data'}
                    </div>
                `;

                const modelStatus = document.getElementById('model-status');
                if (modelStatus) {
                    modelStatus.textContent = 'Demo Mode';
                    modelStatus.className = 'real-data-badge bg-yellow-500';
                }

                Utils.showNotification(connectionResult.message || 'Using demo mode with sample data', 'warning');
            }
        } catch (error) {
            console.error('Connection check error:', error);
            
            connectionDetails.innerHTML = `
                <div class="flex items-center">
                    <div class="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                    <span>Connection Error</span>
                </div>
                <div class="text-red-600 text-xs mt-1">
                    Check backend server
                </div>
            `;
        }
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        this.setupDemoButtons();

       
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

       
        window.addEventListener('online', () => {
            console.log('Connection restored');
            Utils.showNotification('Connection restored', 'success');
            this.checkBackendConnection();
        });

        window.addEventListener('offline', () => {
            console.log('Connection lost');
            Utils.showNotification('Connection lost. Working offline.', 'warning');
        });
    }

    setupDemoButtons() {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            
            if (!loginForm.querySelector('.demo-buttons')) {
                const demoSection = loginForm.querySelector('.bg-gradient-to-r.from-amber-50');
                if (demoSection) {
                    const demoButtons = document.createElement('div');
                    demoButtons.className = 'demo-buttons flex space-x-2 mt-4';
                    demoButtons.innerHTML = `
                        <button type="button" onclick="Auth.demoLogin('farmer')" class="flex-1 bg-green-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-green-600 transition-colors">
                            Login as Farmer
                        </button>
                        <button type="button" onclick="Auth.demoLogin('admin')" class="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
                            Login as Admin
                        </button>
                    `;
                    demoSection.appendChild(demoButtons);
                }
            }
        }
    }

    initializeCharts() {
        console.log('Initializing charts...');
        
        
        const soilCtx = document.getElementById('soilChart');
        if (soilCtx) {
            try {
                this.charts.soil = new Chart(soilCtx.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Nitrogen', 'Phosphorus', 'Potassium', 'Organic Matter'],
                        datasets: [{
                            data: [72, 42, 58, 32],
                            backgroundColor: [
                                'green',
                                'blue',
                                'orange',
                                'purple'
                            ],
                            borderWidth: 2,
                            borderColor: 'white'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 20,
                                    usePointStyle: true
                                }
                            }
                        }
                    }
                });
                console.log('Soil chart initialized');
            } catch (error) {
                console.error('Soil chart error:', error);
            }
        }

        
        const yieldCtx = document.getElementById('yieldChart');
        if (yieldCtx) {
            try {
                this.charts.yield = new Chart(yieldCtx.getContext('2d'), {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                        datasets: [{
                            label: 'Predicted Yield',
                            data: [65, 59, 80, 81, 56, 55, 40],
                            borderColor: 'green',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
                console.log('Yield chart initialized');
            } catch (error) {
                console.error('Yield chart error:', error);
            }
        }
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.classList.remove('modal-open');
    }

    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        console.log('App cleaned up');
    }
}


function openSoilModal() {
    if (window.App) {
        window.App.openModal('soil-modal');
    } else {
        
        const modal = document.getElementById('soil-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    }
}

function openCropModal() {
    if (window.App) {
        window.App.openModal('crop-modal');
    } else {
        
        const modal = document.getElementById('crop-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    }
}

function openFertilizerModal() {
    if (window.App) {
        window.App.openModal('fertilizer-modal');
    } else {
        const modal = document.getElementById('fertilizer-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    }
}

function closeModal(modalId) {
    if (window.App) {
        window.App.closeModal(modalId);
    } else {
       
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }
    }
}


function demoLogin(username = 'farmer') {
    if (window.Auth && typeof window.Auth.demoLogin === 'function') {
        window.Auth.demoLogin(username);
    } else {
        
        const usernameInput = document.getElementById('login-username');
        const passwordInput = document.getElementById('login-password');
        
        const demoCredentials = {
            'farmer': { username: 'farmer', password: 'agrio123' },
            'admin': { username: 'admin', password: 'admin123' }
        };

        if (usernameInput && passwordInput && demoCredentials[username]) {
            usernameInput.value = demoCredentials[username].username;
            passwordInput.value = demoCredentials[username].password;
            Utils.showNotification(`Demo login for ${username}`, 'info');
        }
    }
}


document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing app...');
    window.App = new App();
    await window.App.init();
});