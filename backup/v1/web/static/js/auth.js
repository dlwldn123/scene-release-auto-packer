/**
 * Système d'authentification frontend
 * Gère le token JWT et les requêtes authentifiées
 */

// Récupérer le token depuis localStorage
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Vérifier si utilisateur est connecté
function isAuthenticated() {
    return !!getAuthToken();
}

// Récupérer les données utilisateur depuis localStorage
function getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
}

// Charger les données utilisateur complètes depuis l'API
async function loadUserData() {
    try {
        const response = await authenticatedFetch('/api/auth/me');
        const data = await response.json();
        if (data.success && data.user) {
            localStorage.setItem('user_data', JSON.stringify({
                user_id: data.user.id,
                username: data.user.username,
                role: data.user.role,
                email: data.user.email
            }));
            return data.user;
        }
    } catch (error) {
        console.error('Erreur chargement données utilisateur:', error);
    }
    return null;
}

// Déconnexion
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    window.location.href = '/login';
}

// Requête API avec authentification automatique
async function authenticatedFetch(url, options = {}) {
    const token = getAuthToken();
    
    if (!token) {
        // Rediriger vers login si non authentifié
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
        throw new Error('Non authentifié');
    }
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...(options.headers || {})
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // Si token expiré ou invalide, rediriger vers login
    if (response.status === 401) {
        logout();
        throw new Error('Session expirée');
    }
    
    return response;
}

// API Request Helper avec authentification
async function apiRequest(url, options = {}) {
    try {
        const response = await authenticatedFetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Vérifier l'authentification au chargement de la page
function checkAuth() {
    if (!isAuthenticated() && window.location.pathname !== '/login') {
        window.location.href = '/login';
    } else if (isAuthenticated() && window.location.pathname === '/login') {
        // Si déjà connecté, rediriger vers dashboard
        window.location.href = '/';
    } else if (isAuthenticated() && window.location.pathname !== '/login') {
        // Charger les données utilisateur complètes si connecté
        loadUserData().then(user => {
            if (user) {
                // Afficher menu utilisateur
                const userMenu = document.getElementById('user-menu');
                const usernameDisplay = document.getElementById('username-display');
                if (userMenu && usernameDisplay) {
                    userMenu.style.display = 'flex';
                    usernameDisplay.textContent = user.username;
                }
                
                // Afficher lien gestion utilisateurs si admin
                if (user.role === 'admin') {
                    const usersLink = document.getElementById('users-link');
                    if (usersLink) {
                        usersLink.style.display = 'block';
                    }
                }
            }
        }).catch(() => {});
    }
}

// Vérifier auth immédiatement au chargement
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuth);
} else {
    checkAuth();
}

// Exporter globalement
window.getAuthToken = getAuthToken;
window.isAuthenticated = isAuthenticated;
window.getUserData = getUserData;
window.loadUserData = loadUserData;
window.logout = logout;
window.authenticatedFetch = authenticatedFetch;
window.apiRequest = apiRequest;
window.checkAuth = checkAuth;