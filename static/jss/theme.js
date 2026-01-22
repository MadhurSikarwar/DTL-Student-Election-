/**
 * theme.js - Manages Light/Dark Mode persistence and toggling.
 */

class ThemeManager {
    constructor() {
        this.themeKey = 'student-vote-theme';
        this.html = document.documentElement;
        this.init();
    }

    init() {
        // Check localStorage or system preference
        const savedTheme = localStorage.getItem(this.themeKey);
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme) {
            this.setTheme(savedTheme);
        } else {
            // Default to dark if no preference (since original site was dark)
            this.setTheme(systemPrefersDark ? 'dark' : 'dark');
        }
    }

    setTheme(themeName) {
        this.html.setAttribute('data-theme', themeName);
        localStorage.setItem(this.themeKey, themeName);
        this.updateToggleButton(themeName);
    }

    toggle() {
        const current = this.html.getAttribute('data-theme');
        const newTheme = current === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    updateToggleButton(theme) {
        const btn = document.getElementById('themeToggleBtn');
        if (!btn) return;

        // You can swap icons here
        const icon = btn.querySelector('.theme-icon');
        if (icon) {
            icon.textContent = theme === 'light' ? '☀️' : '🌙';
        }
    }
}

// Initialize immediately to prevent flash
const themeManager = new ThemeManager();

// Expose to window for inline HTML onclick handlers if needed
window.toggleTheme = () => themeManager.toggle();
