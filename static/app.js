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
    handleRoute();
    
    window.addEventListener('hashchange', handleRoute);
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
