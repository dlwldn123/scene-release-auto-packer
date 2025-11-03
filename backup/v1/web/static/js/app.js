/**
 * Modern JavaScript for Scene Packer UI
 * Features:
 * - Dark mode toggle
 * - Smooth scrolling
 * - Toast notifications
 * - Animations
 * - Progress indicators
 */

// API Request Helper - utilise apiRequest depuis auth.js si disponible
// Sinon, utilise la version locale (pour compatibilité)
if (typeof window.apiRequest === 'undefined') {
    window.apiRequest = async function(url, options = {}) {
        try {
            const response = await fetch(url, {
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
    };
}

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container') || this.createContainer();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.id = 'toast-container';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        this.container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
        
        return bsToast;
    }
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration) {
        return this.show(message, 'danger', duration);
    }
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

const toast = new ToastManager();

// Dark Mode Toggle
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }
    
    init() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateIcon();
        this.setupToggle();
    }
    
    setupToggle() {
        const toggle = document.getElementById('theme-toggle');
        if (!toggle) return;
        
        toggle.addEventListener('click', () => {
            this.toggle();
        });
    }
    
    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateIcon();
    }
    
    updateIcon() {
        const icon = document.getElementById('theme-icon');
        if (!icon) return;
        
        icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Smooth Scrolling
function setupSmoothScroll() {
    document.querySelectorAll('a[data-scroll]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href') || link.getAttribute('data-scroll');
            const target = document.querySelector(targetId);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Progress Bar Helper
function updateProgress(progressId, percent) {
    const progressBar = document.querySelector(`#${progressId} .progress-bar`);
    if (progressBar) {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
    }
    
    const progressContainer = document.getElementById(progressId);
    if (progressContainer) {
        progressContainer.style.display = percent > 0 ? 'block' : 'none';
    }
}

// Format Size Helper
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

// Format Date Helper
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce Helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Intersection Observer for Animations
function setupIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, section').forEach(el => {
        observer.observe(el);
    });
}

// Loading Spinner Helper
function createSpinner(size = 'md') {
    const sizes = {
        sm: '20px',
        md: '40px',
        lg: '60px'
    };
    
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.style.width = sizes[size] || sizes.md;
    spinner.style.height = sizes[size] || sizes.md;
    spinner.style.margin = '0 auto';
    return spinner;
}

// Alert Helper with Modern Style
function showAlert(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const alertClass = `alert alert-${type}`;
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    element.innerHTML = `
        <div class="${alertClass} fade-in">
            <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>
            ${message}
        </div>
    `;
    
    // Auto-hide after 5 seconds for success/info
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            const alert = element.querySelector('.alert');
            if (alert) {
                alert.style.transition = 'opacity 0.3s';
                alert.style.opacity = '0';
                setTimeout(() => {
                    element.innerHTML = '';
                }, 300);
            }
        }, 5000);
    }
}

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎨 Scene Packer - Modern UI Loaded');
    
    // Initialize theme manager
    new ThemeManager();
    
    // Setup smooth scrolling
    setupSmoothScroll();
    
    // Setup intersection observer for animations
    setupIntersectionObserver();
    
    // Add animation delay to cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add loading state to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
                
                // Re-enable after 30 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 30000);
            }
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
    
    // Export toast manager globally
    window.toast = toast;
    window.showAlert = showAlert;
    window.updateProgress = updateProgress;
    window.formatSize = formatSize;
    window.formatDate = formatDate;
    window.createSpinner = createSpinner;
});

// Web Vitals Reporting
if (typeof webVitals !== 'undefined') {
    webVitals.onCLS(console.log);
    webVitals.onFID(console.log);
    webVitals.onFCP(console.log);
    webVitals.onLCP(console.log);
    webVitals.onTTFB(console.log);
}