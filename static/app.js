const menuItems = [
    { id: 'dashboard', icon: '🏠', label: 'Meu Painel', path: '#/dashboard' },
    { id: 'favorites', icon: '❤️', label: 'Favoritos', path: '#/favorites' },
    { id: 'alerts', icon: '🔔', label: 'Alertas de preço', path: '#/alerts' },
    { id: 'history', icon: '🕒', label: 'Histórico de buscas', path: '#/history' },
    { id: 'destinations', icon: '📍', label: 'Destinos salvos', path: '#/destinations' },
    { id: 'preferences', icon: '⚙️', label: 'Preferências', path: '#/preferences' }
];

// Initialize UI
function initUI() {
    renderSidebar();
    renderBottomNav();
    setupDropdown();
    setupThemeToggle();
    setupSearchBar();
    handleRoute();
    
    window.addEventListener('hashchange', handleRoute);
}

// Global Toast System
window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="icon">${type === 'success' ? '✅' : '❌'}</span>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// Search Bar Interactive Autocomplete
function setupSearchBar() {
    setupAutocompleteForInput('origin-input', 'origin-autocomplete');
    setupAutocompleteForInput('destination-input', 'destination-autocomplete');
}

function setupAutocompleteForInput(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;
    
    let debounceTimer;
    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if(query.length >= 2) {
            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/v1/flights/airports/cities/search?q=${encodeURIComponent(query)}`);
                    if(res.ok) {
                        const data = await res.json();
                        dropdown.innerHTML = '';
                        if(data.length > 0) {
                            data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'autocomplete-item';
                                div.innerHTML = `✈️ <strong>${item.iata_code}</strong> - ${item.city}, ${item.country}`;
                                div.addEventListener('click', () => {
                                    input.value = `${item.city} (${item.iata_code})`;
                                    dropdown.classList.remove('show');
                                });
                                dropdown.appendChild(div);
                            });
                            dropdown.classList.add('show');
                        } else {
                            dropdown.classList.remove('show');
                        }
                    }
                } catch (err) {
                    console.error('Autocomplete fetch error:', err);
                }
            }, 300);
        } else {
            dropdown.classList.remove('show');
        }
    });

    // Hide dropdown on click outside
    document.addEventListener('click', (e) => {
        if (e.target !== input && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

function renderSidebar() {
    const menuEl = document.getElementById('sidebar-menu');
    menuEl.innerHTML = menuItems.map(item => `
        <li>
            <a href="${item.path}" class="nav-item ${location.hash === item.path || (!location.hash && item.id === 'dashboard') ? 'active' : ''}" data-id="${item.id}">
                <span class="icon">${item.icon}</span> ${item.label}
            </a>
        </li>
    `).join('');
}

function renderBottomNav() {
    const navEl = document.querySelector('.bottom-nav');
    const mobileItems = menuItems.filter(i => ['dashboard', 'favorites', 'alerts', 'history', 'preferences'].includes(i.id));
    navEl.innerHTML = mobileItems.map(item => `
        <a href="${item.path}" class="nav-item ${location.hash === item.path || (!location.hash && item.id === 'dashboard') ? 'active' : ''}" style="flex-direction: column; gap: 4px; padding: 8px;">
            <span class="icon">${item.icon}</span>
            <span style="font-size: 0.65rem;">${item.label.split(' ')[0]}</span>
        </a>
    `).join('');
}

function setupDropdown() {
    const btn = document.getElementById('user-menu-btn');
    const dropdown = document.getElementById('user-dropdown');
    
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

function setupThemeToggle() {
    const switches = document.querySelectorAll('input[type="checkbox"]');
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    document.body.setAttribute('data-theme', savedTheme);
    switches.forEach(s => s.checked = savedTheme === 'dark');

    switches.forEach(s => {
        s.addEventListener('change', (e) => {
            const newTheme = e.target.checked ? 'dark' : 'light';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            switches.forEach(sw => sw.checked = e.target.checked);
        });
    });
}

// Simple Router
import { renderDashboard } from './pages/dashboard.js';
import { renderFavorites } from './pages/favorites.js';
import { renderAlerts } from './pages/alerts.js';
import { renderHistory } from './pages/history.js';
import { renderDestinations } from './pages/destinations.js';
import { renderPreferences } from './pages/preferences.js';

const routes = {
    '#/dashboard': renderDashboard,
    '#/favorites': renderFavorites,
    '#/alerts': renderAlerts,
    '#/history': renderHistory,
    '#/destinations': renderDestinations,
    '#/preferences': renderPreferences,
};

function handleRoute() {
    const path = location.hash || '#/dashboard';
    const contentEl = document.getElementById('page-content');
    
    // Update active state in navs
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll(`.nav-item[href="${path}"]`).forEach(el => el.classList.add('active'));

    // Render content
    if (routes[path]) {
        contentEl.innerHTML = '';
        contentEl.appendChild(routes[path]());
    } else {
        contentEl.innerHTML = `<h2>Em construção</h2><p>A página para ${path} será implementada em breve.</p>`;
    }
}

document.addEventListener('DOMContentLoaded', initUI);
