class Auth {
    constructor() {
        this.user = this.getUser();
    }

    async login(username, password) {
        try {
            const res = await API.login({
                username: username,
                password: password
            });

            if (res.status === 'success') {
                localStorage.setItem('user', JSON.stringify(res.user));
                localStorage.setItem('token', res.token);
                this.user = res.user;
                return { success: true };
            } else {
                return { success: false, message: res.message || 'Login failed' };
            }

        } catch (error) {
            return { success: false, message: 'Login failed' };
        }
    }

    logout() {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        this.user = null;
    }

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    isAuthenticated() {
        return !!localStorage.getItem('token');
    }

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.reload();
        }
    }
}

window.Auth = new Auth();
