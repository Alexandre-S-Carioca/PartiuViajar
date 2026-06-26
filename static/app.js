import { renderDashboard } from './pages/dashboard.js?v=3';
import { renderFavorites } from './pages/favorites.js';
import { renderAlerts } from './pages/alerts.js?v=7';
import { renderHistory } from './pages/history.js';
import { renderDestinations } from './pages/destinations.js';
import { renderPreferences } from './pages/preferences.js';
import { renderTracker } from './pages/tracker.js';

const menuItems = [
    { id: 'dashboard', icon: '🏠', label: 'Meu Painel', path: '#/dashboard' },
    { id: 'tracker', icon: '🛰️', label: 'Rastreio de Voos', path: '#/tracker' },
    { id: 'favorites', icon: '❤️', label: 'Favoritos', path: '#/favorites' },
    { id: 'alerts', icon: '🔔', label: 'Alertas de preço', path: '#/alerts' },
    { id: 'history', icon: '🕒', label: 'Histórico de buscas', path: '#/history' },
    { id: 'preferences', icon: '⚙️', label: 'Preferências', path: '#/preferences' }
];

// Initialize UI
function initUI() {
    // Auth Setup deve ocorrer ANTES de renderizar as rotas e menus
    setupAuth();

    renderSidebar();
    renderBottomNav();
    setupDropdown();
    setupThemeToggle();
    setupSearchBar();
    
    // Restaurar localização salva se houver
    const savedLocation = localStorage.getItem('user_location');
    if (savedLocation) {
        const btnText = document.getElementById('location-text');
        if (btnText) btnText.innerText = savedLocation;
    }
    
    // Remove o fragmento #_=_ que o Facebook injeta no redirecionamento
    if (window.location.hash === '#_=_') {
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    handleRoute();
    
    // Setup tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
        });
    });

    window.addEventListener('hashchange', handleRoute);
    
    window.addEventListener('hashchange', handleRoute);
}

function setupAuth() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
        localStorage.setItem('jwt_token', token);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    updateAuthUI();
}

function updateAuthUI() {
    const token = localStorage.getItem('jwt_token');
    const topbarAvatar = document.getElementById('topbar-avatar');
    const topbarName = document.getElementById('topbar-name');
    const dropAvatar = document.getElementById('dropdown-avatar');
    const dropName = document.getElementById('dropdown-name');
    const dropEmail = document.getElementById('dropdown-email');
    const loginBtn = document.getElementById('menu-login-btn');
    const loginDiv = document.getElementById('menu-login-divider');
    const logoutBtn = document.getElementById('menu-logout-btn');

    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const avatarUrl = payload.avatar || `https://ui-avatars.com/api/?name=${payload.name}&background=0D8ABC&color=fff`;
            
            topbarAvatar.src = avatarUrl;
            topbarName.innerHTML = `Olá, ${payload.name.split(' ')[0]} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`;
            dropAvatar.src = avatarUrl;
            dropName.innerText = payload.name;
            dropEmail.innerText = payload.email;
            
            loginBtn.style.display = 'none';
            loginDiv.style.display = 'none';
            logoutBtn.style.display = 'block';
            document.querySelectorAll('.auth-required').forEach(el => el.style.display = '');
        } catch(e) {
            console.error("Invalid token", e);
            localStorage.removeItem('jwt_token');
        }
    } else {
        topbarAvatar.src = "https://ui-avatars.com/api/?name=Visitante&background=ccc&color=fff";
        topbarName.innerHTML = `Visitante <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`;
        dropAvatar.src = "https://ui-avatars.com/api/?name=Visitante&background=ccc&color=fff";
        dropName.innerText = "Visitante";
        dropEmail.innerText = "Faça login para salvar buscas";
        
        loginBtn.style.display = 'block';
        loginDiv.style.display = 'block';
        logoutBtn.style.display = 'none';
        document.querySelectorAll('.auth-required').forEach(el => el.style.display = 'none');
    }

    // Atualiza menu lateral e inferior baseado no status
    renderSidebar();
    renderBottomNav();
}

window.showAuthModal = function() {
    document.getElementById('user-dropdown').classList.remove('show');
    document.getElementById('auth-modal').classList.add('show');
};

window.logout = function() {
    localStorage.removeItem('jwt_token');
    updateAuthUI();
    window.showToast('Você saiu da sua conta.', 'success');
    // Força a atualização da página para limpar o painel e dados residuais
    setTimeout(() => {
        window.location.reload();
    }, 800);
};


window.currentSearchMode = 'flights';

// Listeners for tabs
document.addEventListener('DOMContentLoaded', () => {
    const tabFlights = document.getElementById('tab-flights');
    const tabHotels = document.getElementById('tab-hotels');
    const originContainer = document.getElementById('origin-container');
    const tripTypeSelector = document.getElementById('flight-trip-type');
    
    const labelCheckin = document.getElementById('label-checkin');
    const labelCheckout = document.getElementById('label-checkout');
    const labelGuests = document.getElementById('label-guests');

    if(tabFlights) {
        tabFlights.addEventListener('click', () => {
            window.currentSearchMode = 'flights';
            originContainer.style.display = 'block';
            if(tripTypeSelector) tripTypeSelector.style.display = 'block';
            if(labelCheckin) labelCheckin.innerText = 'IDA';
            if(labelCheckout) labelCheckout.innerText = 'VOLTA';
            if(labelGuests) labelGuests.innerText = 'PASSAGEIROS';
        });
    }
    if(tabHotels) {
        tabHotels.addEventListener('click', () => {
            window.currentSearchMode = 'hotels';
            originContainer.style.display = 'none';
            if(tripTypeSelector) tripTypeSelector.style.display = 'none';
            if(labelCheckin) labelCheckin.innerText = 'CHECK-IN';
            if(labelCheckout) labelCheckout.innerText = 'CHECK-OUT';
            if(labelGuests) labelGuests.innerText = 'HÓSPEDES';
        });
    }

    const tripRadios = document.querySelectorAll('input[name="trip_type"]');
    if(tripRadios.length > 0) {
        tripRadios.forEach(r => r.addEventListener('change', (e) => {
            const checkoutWrapper = document.getElementById('checkout-wrapper');
            if(e.target.value === 'oneway') {
                if(checkoutWrapper) checkoutWrapper.style.display = 'none';
                document.getElementById('checkout-input').value = '';
            } else {
                if(checkoutWrapper) checkoutWrapper.style.display = 'flex';
            }
        }));
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

// Save Search to History
window.saveSearchHistory = function(mode, origin, dest, checkin) {
    try {
        let history = JSON.parse(localStorage.getItem('partiuviajar_history') || '[]');
        
        let destName = dest ? dest.split('(')[0].trim() : 'Desconhecido';
        let originName = origin ? origin.split('(')[0].trim() : '';
        
        let text = mode === 'hotels' ? `Hotéis em ${destName}` : `${originName} → ${destName}`;
        
        let parts = checkin.split('-');
        let dateStr = parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : checkin;

        const entry = { mode, text, date: dateStr, ts: Date.now() };
        
        if(history.length > 0 && history[0].text === entry.text && history[0].date === entry.date) {
            return;
        }

        history.unshift(entry);
        if(history.length > 5) history.pop();
        
        localStorage.setItem('partiuviajar_history', JSON.stringify(history));
    } catch(e) {
        console.error("Erro ao salvar histórico", e);
    }
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

        window.saveSearchHistory('hotels', originRaw, destRaw, checkin);

        const overlay = document.getElementById('search-results-overlay');
        const body = document.getElementById('search-results-body');
        overlay.classList.add('show');
        
        body.innerHTML = `
            <div style="margin-bottom: 30px;">
                <div class="skeleton skeleton-title" style="width: 60%; max-width: 300px; margin-bottom: 15px;"></div>
                ${[1, 2, 3].map(() => `
                <div class="result-card skeleton-wrapper">
                    <div class="skeleton skeleton-card" style="width: 80px; height: 80px; flex-shrink: 0;"></div>
                    <div class="info-section" style="width: 100%;">
                        <div class="skeleton skeleton-text" style="width: 70%; height: 20px; margin-bottom: 10px;"></div>
                        <div class="skeleton skeleton-text" style="width: 50%; margin-bottom: 6px;"></div>
                        <div class="skeleton skeleton-text" style="width: 40%;"></div>
                    </div>
                    <div class="price-section" style="min-width: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div class="skeleton skeleton-text" style="width: 100%; height: 24px; align-self: flex-end;"></div>
                        <div class="skeleton skeleton-card" style="width: 100%; height: 32px; border-radius: 4px; margin-top: 8px;"></div>
                    </div>
                </div>
                `).join('')}
            </div>
        `;

        try {
            let url = `/api/hotels?destination=${destCode}&checkin=${checkin}&checkout=${checkout}&adults=${adults}`;
            const token = localStorage.getItem('jwt_token');
            const headers = token ? { "Authorization": `Bearer ${token}` } : {};
            
            const res = await fetch(url, { headers });
            
            if(res.status === 403) {
                window.showAuthModal();
                throw new Error('Limite gratuito excedido');
            }
            if(!res.ok) throw new Error('Erro na busca');
            const data = await res.json();

            let hotelsHtml = '';
            if(data && data.length > 0) {
                hotelsHtml = data.map(h => `
                    <div class="result-card">
                        <img src="${h.photo_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=100&q=80'}" class="hotel-thumb">
                        <div class="info-section">
                            <strong style="color: var(--primary); font-size: 1.1rem;">${h.name}</strong> 
                            <span style="color: #F59E0B; margin-left: 8px;">${'★'.repeat(h.stars || 0)}${'☆'.repeat(Math.max(0, 5-(h.stars || 0)))}</span><br>
                            <span style="font-size: 0.9rem; color: var(--text-secondary)">${(h.type || 'Hotel').toUpperCase()} • Nota: ${h.rating}/10 (${h.reviews_count || 0} avaliações)</span><br>
                            <span style="font-size: 0.85rem; color: var(--text-secondary)">A ${h.distance_center}km do centro</span>
                        </div>
                        <div class="price-section">
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

    window.saveSearchHistory('flights', originRaw, destRaw, checkin);

    const overlay = document.getElementById('search-results-overlay');
    const body = document.getElementById('search-results-body');
    overlay.classList.add('show');
    
    body.innerHTML = `
        <div style="margin-bottom: 30px;">
            <div class="skeleton skeleton-title" style="width: 70%; max-width: 350px; margin-bottom: 15px;"></div>
            ${[1, 2, 3].map(() => `
            <div class="result-card skeleton-wrapper">
                <div class="info-section" style="width: 100%;">
                    <div class="skeleton skeleton-text" style="width: 30%; height: 18px; margin-bottom: 12px;"></div>
                    <div class="skeleton skeleton-text" style="width: 60%; height: 14px; margin-bottom: 8px;"></div>
                    <div class="skeleton skeleton-text" style="width: 40%; height: 12px;"></div>
                </div>
                <div class="price-section" style="min-width: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div class="skeleton skeleton-text" style="width: 100%; height: 26px; align-self: flex-end;"></div>
                    <div class="skeleton skeleton-card" style="width: 100%; height: 35px; border-radius: 4px; margin-top: 8px;"></div>
                </div>
            </div>
            `).join('')}
        </div>
    `;

    try {
        let url = `/api/travel?origin=${originCode}&destination=${destCode}&departure_date=${checkin}&adults=${adults}`;
        if(checkout) url += `&return_date=${checkout}`;

        const token = localStorage.getItem('jwt_token');
        const headers = token ? { "Authorization": `Bearer ${token}` } : {};
            
        const res = await fetch(url, { headers });
        if(res.status === 403) {
            window.showAuthModal();
            throw new Error('Limite gratuito excedido');
        }
        if(!res.ok) throw new Error('Erro na busca');
        const data = await res.json();

        let flightsHtml = '';
        if(data.flights && data.flights.outbound && data.flights.outbound.length > 0) {
            flightsHtml = data.flights.outbound.map(f => `
                <div class="result-card">
                    <div class="info-section">
                        <strong style="color: var(--primary)">${f.airline}</strong><br>
                        <span>${new Date(f.departure_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${new Date(f.arrival_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        <div style="font-size: 0.8rem; color: var(--text-secondary)">${f.origin} → ${f.destination} (${f.duration})</div>
                    </div>
                    <div class="price-section">
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
                <div class="result-card">
                    <img src="${h.photo_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=100&q=80'}" class="hotel-thumb">
                    <div class="info-section">
                        <strong style="color: var(--primary); font-size: 1.1rem;">${h.name}</strong> 
                        <span style="color: #F59E0B; margin-left: 8px;">${'★'.repeat(h.stars || 0)}${'☆'.repeat(Math.max(0, 5-(h.stars || 0)))}</span><br>
                        <span style="font-size: 0.9rem; color: var(--text-secondary)">${(h.type || 'Hotel').toUpperCase()} • Nota: ${h.rating}/10 (${h.reviews_count || 0} avaliações)</span><br>
                        <span style="font-size: 0.85rem; color: var(--text-secondary)">A ${h.distance_center}km do centro</span>
                    </div>
                    <div class="price-section">
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
    window.setupAutocompleteForInput('origin-input', 'origin-autocomplete');
    window.setupAutocompleteForInput('destination-input', 'destination-autocomplete');
}

window.setupAutocompleteForInput = function(inputId, dropdownId) {
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
    if (!menuEl) return;
    const token = localStorage.getItem('jwt_token');
    const authOnlyIds = ['favorites', 'alerts', 'history', 'destinations'];
    const items = menuItems.filter(item => token || !authOnlyIds.includes(item.id));
    
    menuEl.innerHTML = items.map(item => `
        <li>
            <a href="${item.path}" class="nav-item ${location.hash === item.path || (!location.hash && item.id === 'dashboard') ? 'active' : ''}" data-id="${item.id}">
                <span class="icon">${item.icon}</span> ${item.label}
            </a>
        </li>
    `).join('');
}

function renderBottomNav() {
    const navEl = document.querySelector('.bottom-nav');
    if (!navEl) return;
    const token = localStorage.getItem('jwt_token');
    const authOnlyIds = ['favorites', 'alerts', 'history', 'destinations'];
    const mobileItems = menuItems.filter(i => ['dashboard', 'favorites', 'alerts', 'history', 'preferences'].includes(i.id) && (token || !authOnlyIds.includes(i.id)));
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
    const btns = document.querySelectorAll('.theme-toggle');
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    document.body.setAttribute('data-theme', savedTheme);
    
    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            const current = document.body.getAttribute('data-theme');
            const newTheme = current === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            // Muda o ícone
            btns.forEach(b => {
                b.innerHTML = newTheme === 'dark' ? '🌙' : '☀️';
            });
        });
        
        // Define icone inicial
        btn.innerHTML = savedTheme === 'dark' ? '🌙' : '☀️';
    });
}

// Simple Router

const routes = {
    '#/dashboard': renderDashboard,
    '#/tracker': renderTracker,
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

    // Toggle search bar visibility based on route
    const isDashboard = (path === '#/dashboard');
    const tabs = document.querySelector('.topbar-tabs');
    const tripType = document.getElementById('flight-trip-type');
    const searchBar = document.querySelector('.search-bar-container');
    
    if (tabs) tabs.style.display = isDashboard ? 'flex' : 'none';
    if (tripType) tripType.style.display = isDashboard ? 'block' : 'none';
    if (searchBar) searchBar.style.display = isDashboard ? 'flex' : 'none';

    // Render content
    if (routes[path]) {
        contentEl.innerHTML = '';
        contentEl.appendChild(routes[path]());
    } else {
        contentEl.innerHTML = `<h2>Em construção</h2><p>A página para ${path} será implementada em breve.</p>`;
    }
}

window.resetSearchAndHome = function() {
    window.location.hash = '#/dashboard';
    
    const overlay = document.getElementById('search-results-overlay');
    if (overlay) overlay.classList.remove('show');
    
    const origin = document.getElementById('origin-input');
    if (origin) origin.value = '';
    
    const dest = document.getElementById('destination-input');
    if (dest) dest.value = '';
};

window.locateMe = function() {
    const btnText = document.getElementById('location-text');
    if ("geolocation" in navigator) {
        if(btnText) btnText.innerText = "Buscando...";
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            window.showToast("Localização encontrada!", "success");
            
            // Reverse Geocoding
            try {
                const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                if(resp.ok) {
                    const data = await resp.json();
                    if(data && data.address) {
                        const city = data.address.city || data.address.town || data.address.municipality || 'Desconhecido';
                        const state = data.address.state || '';
                        if(btnText) btnText.innerText = `${city}-${state}`;
                        localStorage.setItem('user_location', `${city}-${state}`);
                        localStorage.setItem('user_lat', lat);
                        localStorage.setItem('user_lon', lon);
                    } else {
                        if(btnText) btnText.innerText = 'Localização';
                    }
                }
            } catch(e) {
                if(btnText) btnText.innerText = 'Localização';
            }
            
            if (window._dashboardMap) {
                window._dashboardMap.setView([lat, lon], 12);
                L.marker([lat, lon]).addTo(window._dashboardMap).bindPopup('Você está aqui!').openPopup();
            } else {
                window.location.hash = '#/dashboard';
                setTimeout(() => {
                    if (window._dashboardMap) {
                        window._dashboardMap.setView([lat, lon], 12);
                        L.marker([lat, lon]).addTo(window._dashboardMap).bindPopup('Você está aqui!').openPopup();
                    }
                }, 500);
            }
        }, (error) => {
            if(btnText) btnText.innerText = 'Localização';
            window.showToast("Erro ao obter localização. Permissão negada ou indisponível.", "error");
        }, {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        });
    } else {
        window.showToast("Seu navegador não suporta geolocalização.", "error");
    }
};

window.searchMapDestination = async function() {
    const input = document.getElementById('map-search-input');
    if (!input || !input.value.trim()) return;
    
    const query = input.value.trim();
    window.showToast("Buscando destino...", "info");
    
    try {
        const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`);
        const data = await resp.json();
        
        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);
            window.showToast(`Destino encontrado: ${data[0].display_name.split(',')[0]}`, "success");
            
            if (window._dashboardMap) {
                window._dashboardMap.setView([lat, lon], 12);
            } else {
                window.location.hash = '#/dashboard';
                setTimeout(() => {
                    if (window._dashboardMap) {
                        window._dashboardMap.setView([lat, lon], 12);
                    }
                }, 500);
            }
        } else {
            window.showToast("Destino não encontrado.", "error");
        }
    } catch (e) {
        window.showToast("Erro ao buscar o destino.", "error");
    }
};

window.toggleMapFullscreen = function() {
    const mapContainer = document.getElementById('dashboard-map');
    if (!mapContainer) return;
    
    // Injeta o estilo do mapa suspenso (modal) se não existir
    if (!document.getElementById('map-suspended-style')) {
        const style = document.createElement('style');
        style.id = 'map-suspended-style';
        style.innerHTML = `
            .map-suspended {
                position: fixed !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                width: 85vw !important;
                height: 85vh !important;
                z-index: 9999 !important;
                box-shadow: 0 0 0 100vw rgba(0,0,0,0.7), 0 10px 40px rgba(0,0,0,0.5) !important;
                border-radius: 16px !important;
                border: 2px solid var(--border-color) !important;
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            }
        `;
        document.head.appendChild(style);
    }
    
    mapContainer.classList.toggle('map-suspended');
    
    // Cria ou atualiza o botão X (Fechar) dentro do mapa
    let closeBtn = document.getElementById('map-close-btn');
    if (mapContainer.classList.contains('map-suspended')) {
        if (!closeBtn) {
            closeBtn = document.createElement('button');
            closeBtn.id = 'map-close-btn';
            closeBtn.innerHTML = '✖';
            closeBtn.title = 'Sair do Modo Suspenso';
            closeBtn.style.cssText = 'position: absolute; top: 16px; right: 16px; z-index: 10000; background: var(--bg-primary); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 50%; width: 40px; height: 40px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.4);';
            // Impede que o clique no botão vaze para o Leaflet
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                window.toggleMapFullscreen();
            });
            mapContainer.appendChild(closeBtn);
        }
        closeBtn.style.display = 'flex';
    } else {
        if (closeBtn) closeBtn.style.display = 'none';
    }
    
    if (window._dashboardMap) {
        // Dá um tempo para a transição do CSS antes de forçar a re-renderização do Leaflet
        setTimeout(() => window._dashboardMap.invalidateSize(), 350);
    }
};

document.addEventListener('DOMContentLoaded', initUI);
