
class Auth {
    constructor() {
        this.currentUser = null;
        this.isLoggedIn = false;
    }

    async init() {
        await this.checkLoginStatus();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const loginForm = document.getElementById('login-form');
        const logoutBtn = document.getElementById('logout-btn');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }
    }

    async checkLoginStatus() {
        try {
            const userData = await API.getCurrentUser();
            if (userData) {
                this.currentUser = userData.user;
                this.isLoggedIn = true;
                this.showDashboard();
                this.updateUserInterface();
            } else {
                this.showLoginPage();
            }
        } catch (error) {
            console.error('Error checking login status:', error);
            this.showLoginPage();
        }
    }

    async handleLogin(event) {
        event.preventDefault();

        const username = document.getElementById('login-username')?.value.trim();
        const password = document.getElementById('login-password')?.value;

        if (!username || !password) {
            Utils.showNotification('Please enter both username and password', 'warning');
            return;
        }

        const loginBtn = event.target.querySelector('button[type="submit"]');
        const originalText = Utils.showLoading(loginBtn, 'Signing in...');

        try {
            const result = await API.login({ username, password });

            if (result.success) {
                this.currentUser = result.user;
                this.isLoggedIn = true;

                Utils.showNotification(result.message, 'success');
                this.showDashboard();
                this.updateUserInterface();

                
                const loginForm = document.getElementById('login-form');
                if (loginForm) loginForm.reset();

            } else {
                Utils.showNotification(result.error || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            Utils.showNotification('Login failed. Please try again.', 'error');
        } finally {
            Utils.hideLoading(loginBtn, originalText);
        }
    }

    async handleLogout() {
        try {
            await API.logout();
            this.currentUser = null;
            this.isLoggedIn = false;

            Utils.showNotification('Logged out successfully', 'success');
            this.showLoginPage();

        } catch (error) {
            console.error('Logout error:', error);
            Utils.showNotification('Logout failed', 'error');
        }
    }

    showLoginPage() {
        const loginPage = document.getElementById('login-page');
        const dashboard = document.getElementById('dashboard');
        
        if (loginPage) loginPage.classList.remove('hidden');
        if (dashboard) dashboard.classList.add('hidden');
        
        document.body.classList.remove('modal-open');
    }

    showDashboard() {
        const loginPage = document.getElementById('login-page');
        const dashboard = document.getElementById('dashboard');
        
        if (loginPage) loginPage.classList.add('hidden');
        if (dashboard) dashboard.classList.remove('hidden');
    }

    updateUserInterface() {
        if (!this.currentUser) return;

        const userGreeting = document.getElementById('user-greeting');
        if (userGreeting) {
            userGreeting.textContent = `Welcome, ${this.currentUser.name.split(' ')[0]}!`;
        }
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isAuthenticated() {
        return this.isLoggedIn;
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            this.showLoginPage();
            Utils.showNotification('Please log in to continue', 'warning');
            return false;
        }
        return true;
    }

    async demoLogin(username = 'farmer') {
        const demoCredentials = {
            'farmer': { username: 'farmer', password: 'agrio123' },
            'admin': { username: 'admin', password: 'admin123' },
            'user1': { username: 'user1', password: 'pass123' }
        };

        if (!demoCredentials[username]) {
            Utils.showNotification('Invalid demo user', 'error');
            return;
        }

        const usernameInput = document.getElementById('login-username');
        const passwordInput = document.getElementById('login-password');
        
        if (usernameInput && passwordInput) {
            usernameInput.value = demoCredentials[username].username;
            passwordInput.value = demoCredentials[username].password;
        }

        
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            const event = new Event('submit', { bubbles: true, cancelable: true });
            loginForm.dispatchEvent(event);
        }
    }
}

window.Auth = new Auth();