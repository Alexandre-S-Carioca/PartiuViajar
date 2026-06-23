import { renderDashboard } from './pages/dashboard.js';
import { renderFavorites } from './pages/favorites.js';
import { renderAlerts } from './pages/alerts.js';
import { renderHistory } from './pages/history.js';
import { renderDestinations } from './pages/destinations.js';
import { renderPreferences } from './pages/preferences.js';

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
    
    // Setup tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
        });
    });

    window.addEventListener('hashchange', handleRoute);
}

window.currentSearchMode = 'flights';

// Listeners for tabs
document.addEventListener('DOMContentLoaded', () => {
    const tabFlights = document.getElementById('tab-flights');
    const tabHotels = document.getElementById('tab-hotels');
    const originContainer = document.getElementById('origin-container');

    if(tabFlights) {
        tabFlights.addEventListener('click', () => {
            window.currentSearchMode = 'flights';
            originContainer.style.display = 'block';
        });
    }
    if(tabHotels) {
        tabHotels.addEventListener('click', () => {
            window.currentSearchMode = 'hotels';
            originContainer.style.display = 'none';
        });
    }
});

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

// Perform Actual Search
window.performSearch = async function() {
    const originRaw = document.getElementById('origin-input').value;
    const destRaw = document.getElementById('destination-input').value;
    const checkin = document.getElementById('checkin-input').value;
    const checkout = document.getElementById('checkout-input').value;
    const adults = document.getElementById('adults-input').value || 1;

    // Extract IATA codes. Assuming format "City (IATA)"
    const extractIata = (str) => {
        const match = str.match(/\(([A-Z]{3})\)/);
        return match ? match[1] : str.substring(0,3).toUpperCase();
    };

    const originCode = extractIata(originRaw);
    const destCode = extractIata(destRaw);

    if (window.currentSearchMode === 'hotels') {
        if(!destCode || !checkin || !checkout) {
            window.showToast('Por favor, preencha destino, data de check-in e check-out.', 'error');
            return;
        }

        const overlay = document.getElementById('search-results-overlay');
        const body = document.getElementById('search-results-body');
        overlay.classList.add('show');
        
        body.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <div class="typing-indicator" style="margin-bottom: 20px;"><span></span><span></span><span></span></div>
                <h4>Buscando os melhores hotéis e acomodações...</h4>
                <p style="color: var(--text-secondary)">Isso pode levar alguns segundos.</p>
            </div>
        `;

        try {
            let url = `/api/hotels?destination=${destCode}&checkin=${checkin}&checkout=${checkout}&adults=${adults}`;
            const res = await fetch(url);
            if(!res.ok) throw new Error('Erro na busca');
            const data = await res.json();

            let hotelsHtml = '';
            if(data && data.length > 0) {
                hotelsHtml = data.map(h => `
                    <div style="background: var(--bg-main); padding: 16px; border-radius: 8px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); display: flex; gap: 16px; align-items: center;">
                        <img src="${h.photo_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=100&q=80'}" style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover;">
                        <div style="flex: 1;">
                            <strong style="color: var(--primary); font-size: 1.1rem;">${h.name}</strong> 
                            <span style="color: #F59E0B; margin-left: 8px;">${'★'.repeat(h.stars || 0)}${'☆'.repeat(Math.max(0, 5-(h.stars || 0)))}</span><br>
                            <span style="font-size: 0.9rem; color: var(--text-secondary)">${(h.type || 'Hotel').toUpperCase()} • Nota: ${h.rating}/10 (${h.reviews_count || 0} avaliações)</span><br>
                            <span style="font-size: 0.85rem; color: var(--text-secondary)">A ${h.distance_center}km do centro</span>
                        </div>
                        <div style="text-align: right; min-width: 120px;">
                            <span style="font-size: 0.8rem; color: var(--text-secondary)">Diária a partir de</span><br>
                            <strong style="font-size: 1.2rem; color: var(--success)">R$ ${parseFloat(h.price_per_night).toFixed(2)}</strong><br>
                            <a href="https://www.google.com/travel/search?q=${encodeURIComponent('Hotel ' + h.name)}" target="_blank" rel="noopener noreferrer" class="btn-magic" style="padding: 6px 12px; font-size: 0.85rem; margin-top: 8px; width: 100%; display: block; text-align: center; text-decoration: none;">Reservar</a>
                        </div>
                    </div>
                `).join('');
            } else {
                hotelsHtml = '<p>Nenhuma hospedagem encontrada para este destino e data.</p>';
            }

            body.innerHTML = `
                <div style="margin-bottom: 30px;">
                    <h4 style="margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">🏨 Hospedagens encontradas em ${destRaw.split(',')[0]}</h4>
                    ${hotelsHtml}
                </div>
            `;
        } catch(err) {
            body.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--danger);">
                    <h4>Ops! Ocorreu um erro ao buscar hospedagens.</h4>
                    <p>Verifique a conexão ou tente novamente mais tarde.</p>
                </div>
            `;
        }
        return;
    }

    // Fluxo original de passagens (unified_search)
    if(!originCode || !destCode || !checkin) {
        window.showToast('Por favor, preencha origem, destino e data de ida.', 'error');
        return;
    }

    const overlay = document.getElementById('search-results-overlay');
    const body = document.getElementById('search-results-body');
    overlay.classList.add('show');
    
    body.innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <div class="typing-indicator" style="margin-bottom: 20px;"><span></span><span></span><span></span></div>
            <h4>Buscando as melhores opções em várias companhias...</h4>
            <p style="color: var(--text-secondary)">Isso pode levar alguns segundos, o Partiu Viajar está vasculhando a internet.</p>
        </div>
    `;

    try {
        let url = `/api/travel?origin=${originCode}&destination=${destCode}&departure_date=${checkin}&adults=${adults}`;
        if(checkout) url += `&return_date=${checkout}`;

        const res = await fetch(url);
        if(!res.ok) throw new Error('Erro na busca');
        const data = await res.json();

        let flightsHtml = '';
        if(data.flights && data.flights.outbound && data.flights.outbound.length > 0) {
            flightsHtml = data.flights.outbound.map(f => `
                <div style="background: var(--bg-main); padding: 16px; border-radius: 8px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: var(--primary)">${f.airline}</strong><br>
                        <span>${new Date(f.departure_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${new Date(f.arrival_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        <div style="font-size: 0.8rem; color: var(--text-secondary)">${f.origin} → ${f.destination} (${f.duration})</div>
                    </div>
                    <div style="text-align: right;">
                        <strong style="font-size: 1.2rem; color: var(--success)">R$ ${parseFloat(f.price).toFixed(2)}</strong><br>
                        <a href="${f.booking_url}" target="_blank" rel="noopener noreferrer" class="btn-magic" style="padding: 8px 16px; font-size: 0.9rem; margin-top: 8px; display: inline-block; text-decoration: none; position: relative; z-index: 9999;">Comprar</a>
                    </div>
                </div>
            `).join('');
        } else {
            flightsHtml = '<p>Nenhum voo encontrado para esta rota.</p>';
        }

        let hotelsHtml = '';
        if(data.accommodations && data.accommodations.length > 0) {
            hotelsHtml = data.accommodations.map(h => `
                <div style="background: var(--bg-main); padding: 16px; border-radius: 8px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); display: flex; gap: 16px; align-items: center;">
                    <img src="${h.photo_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=100&q=80'}" style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover;">
                    <div style="flex: 1;">
                        <strong style="color: var(--primary); font-size: 1.1rem;">${h.name}</strong> 
                        <span style="color: #F59E0B; margin-left: 8px;">${'★'.repeat(h.stars || 0)}${'☆'.repeat(Math.max(0, 5-(h.stars || 0)))}</span><br>
                        <span style="font-size: 0.9rem; color: var(--text-secondary)">${(h.type || 'Hotel').toUpperCase()} • Nota: ${h.rating}/10 (${h.reviews_count || 0} avaliações)</span><br>
                        <span style="font-size: 0.85rem; color: var(--text-secondary)">A ${h.distance_center}km do centro</span>
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary)">Diária a partir de</span><br>
                        <strong style="font-size: 1.2rem; color: var(--success)">R$ ${parseFloat(h.price_per_night).toFixed(2)}</strong><br>
                        <a href="https://www.google.com/travel/search?q=${encodeURIComponent('Hotel ' + h.name)}" target="_blank" rel="noopener noreferrer" class="btn-magic" style="padding: 6px 12px; font-size: 0.85rem; margin-top: 8px; width: 100%; display: block; text-align: center; text-decoration: none;">Reservar</a>
                    </div>
                </div>
            `).join('');
        } else {
            hotelsHtml = '<p>Nenhuma hospedagem encontrada para este destino.</p>';
        }

        body.innerHTML = `
            <div style="margin-bottom: 30px;">
                <h4 style="margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">✈️ Voos de Ida encontrados para ${destRaw.split(',')[0]}</h4>
                ${flightsHtml}
            </div>
            <div>
                <h4 style="margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">🏨 Hospedagens em ${destRaw.split(',')[0]}</h4>
                ${hotelsHtml}
            </div>
        `;

    } catch(err) {
        body.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--danger);">
                <h4>Ops! Ocorreu um erro ao buscar passagens.</h4>
                <p>Verifique se o backend (flight_engine) está rodando e se há internet.</p>
            </div>
        `;
    }
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

    const performAutocomplete = async (query) => {
        try {
            // Se estiver vazio, exibe alguns populares como default
            let url = `/api/v1/flights/airports/cities/search?q=${encodeURIComponent(query)}`;
            if(query.length === 0) {
                // Mock de populares se vazio
                dropdown.innerHTML = `
                    <div class="autocomplete-item" data-val="São Paulo (GRU)">✈️ <strong>GRU</strong> - São Paulo, Brasil</div>
                    <div class="autocomplete-item" data-val="Rio de Janeiro (GIG)">✈️ <strong>GIG</strong> - Rio de Janeiro, Brasil</div>
                    <div class="autocomplete-item" data-val="Lisboa (LIS)">✈️ <strong>LIS</strong> - Lisboa, Portugal</div>
                    <div class="autocomplete-item" data-val="Miami (MIA)">✈️ <strong>MIA</strong> - Miami, Estados Unidos</div>
                `;
                dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
                    el.addEventListener('click', () => {
                        input.value = el.getAttribute('data-val');
                        dropdown.classList.remove('show');
                    });
                });
                dropdown.classList.add('show');
                return;
            }

            const res = await fetch(url);
            if(res.ok) {
                const data = await res.json();
                dropdown.innerHTML = '';
                if(data.length > 0) {
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'autocomplete-item';
                        div.innerHTML = `✈️ <strong>${item.code}</strong> - ${item.city}, ${item.country}`;
                        div.addEventListener('click', () => {
                            input.value = `${item.city} (${item.code})`;
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
    };

    input.addEventListener('focus', () => {
        performAutocomplete(input.value.trim());
    });

    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if(query.length >= 2 || query.length === 0) {
            debounceTimer = setTimeout(() => performAutocomplete(query), 300);
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
