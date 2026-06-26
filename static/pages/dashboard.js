export function renderDashboard() {
    const container = document.createElement('div');
    container.className = 'dashboard-container';

    const token = localStorage.getItem('jwt_token');
    
    let userName = "Visitante";
    let userAvatar = "https://ui-avatars.com/api/?name=Visitante&background=ccc&color=fff&size=80";
    let memberSince = "Visitante";
    
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            userName = payload.name.split(' ')[0];
            userAvatar = payload.avatar || `https://ui-avatars.com/api/?name=${payload.name}&background=0D8ABC&color=fff&size=80`;
            memberSince = "Membro ativo";
        } catch(e) {}
    }

    let premiumContent = '';

    let history = [];
    try {
        history = JSON.parse(localStorage.getItem('partiuviajar_history') || '[]');
    } catch(e) {}
    let historyCount = history.length;

    if (token) {
        premiumContent = `
        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card" style="--bg: var(--card-search-bg); --icon-color: var(--card-search-icon)">
                <div class="icon-box">🔍</div>
                <div class="stat-info">
                    <h3>${historyCount}</h3>
                    <p>Pesquisas realizadas</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-fav-bg); --icon-color: var(--card-fav-icon)">
                <div class="icon-box">❤️</div>
                <div class="stat-info">
                    <h3>0</h3>
                    <p>Favoritos salvos</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-alert-bg); --icon-color: var(--card-alert-icon)">
                <div class="icon-box">🔔</div>
                <div class="stat-info">
                    <h3>0</h3>
                    <p>Alertas ativos de preço</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-dest-bg); --icon-color: var(--card-dest-icon)">
                <div class="icon-box">📍</div>
                <div class="stat-info">
                    <h3>0</h3>
                    <p>Destinos salvos</p>
                </div>
            </div>
        </div>

        <!-- 3 Columns Layout -->
        <div class="three-cols-grid">
            <!-- Price Alerts -->
            <div class="dashboard-panel">
                <div class="panel-header">
                    <h3>Alertas de preço ativos</h3>
                    <a href="#/alerts" class="link-btn">Ver todos</a>
                </div>
                <div class="panel-content" style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 40px 20px; color: var(--text-secondary);">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🔔</div>
                    <p>Você ainda não possui nenhum alerta de preço ativo.</p>
                </div>
            </div>

            <!-- Recent Searches -->
            <div class="dashboard-panel">
                <div class="panel-header">
                    <h3>Últimas buscas</h3>
                    <a href="#/history" class="link-btn">Ver histórico</a>
                </div>
                ${historyCount === 0 ? `
                <div class="panel-content list-content" style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 40px 20px; color: var(--text-secondary);">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🕒</div>
                    <p>O seu histórico de buscas está vazio. Que tal começar a explorar?</p>
                </div>
                ` : `
                <div class="panel-content list-content">
                    ${history.map(item => `
                        <div class="history-item">
                            <span class="icon">🕒</span> <span class="text">${item.text}</span> <span class="date">${item.date}</span>
                        </div>
                    `).join('')}
                    <button class="btn-outline full-width mt-10">Buscar novamente</button>
                </div>
                `}
            </div>

            <!-- Interactive Map -->
            <div class="dashboard-panel" style="display: flex; flex-direction: column;">
                <div class="panel-header" style="flex-shrink: 0; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">Mapa de Destinos</h3>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="text" id="map-search-input" placeholder="Ex: Paris, Tóquio..." style="padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-primary); color: var(--text-primary); font-size: 0.85rem; width: 160px;" onkeypress="if(event.key === 'Enter') window.searchMapDestination()">
                        <button onclick="window.searchMapDestination()" style="padding: 6px 12px; border-radius: 6px; background: var(--primary-color); color: white; border: none; cursor: pointer; font-size: 0.85rem;">Buscar</button>
                    </div>
                </div>
                <div class="panel-content" style="flex: 1; padding: 0;">
                    <div id="dashboard-map" style="width: 100%; min-height: 450px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; z-index: 1;"></div>
                </div>
            </div>
        </div>

        <!-- Recommended section -->
        <div class="recommended-section">
            <div class="panel-header mb-15">
                <h3>Recomendado para você</h3>
                <a href="#" class="link-btn">Ver mais recomendações</a>
            </div>
            <div class="cards-carousel">
                <!-- Card 1 -->
                <a href="https://www.google.com/travel/search?q=Porto+de+Galinhas" target="_blank" style="text-decoration: none; color: inherit; display: block;" class="rec-card">
                    <img src="https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?auto=format&fit=crop&w=300&q=80" alt="Porto de Galinhas">
                    <div class="rec-info">
                        <h4>Porto de Galinhas</h4>
                        <span class="loc">Pernambuco</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 540</strong>
                        </div>
                    </div>
                </a>
                <!-- Card 2 -->
                <a href="https://www.google.com/travel/search?q=Maceio" target="_blank" style="text-decoration: none; color: inherit; display: block;" class="rec-card">
                    <img src="https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?auto=format&fit=crop&w=300&q=80" alt="Maceió">
                    <div class="rec-info">
                        <h4>Maceió</h4>
                        <span class="loc">Alagoas</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 480</strong>
                        </div>
                    </div>
                </a>
                <!-- Card 3 -->
                <a href="https://www.google.com/travel/search?q=Sao+Paulo" target="_blank" style="text-decoration: none; color: inherit; display: block;" class="rec-card">
                    <img src="https://images.unsplash.com/photo-1543007630-9710e4a00a20?auto=format&fit=crop&w=300&q=80" alt="São Paulo">
                    <div class="rec-info">
                        <h4>São Paulo</h4>
                        <span class="loc">São Paulo</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 430</strong>
                        </div>
                    </div>
                </a>
                <!-- Card 4 -->
                <a href="https://www.google.com/travel/search?q=Lisboa" target="_blank" style="text-decoration: none; color: inherit; display: block;" class="rec-card">
                    <img src="https://images.unsplash.com/photo-1585208798174-6cedd86e019a?auto=format&fit=crop&w=300&q=80" alt="Lisboa">
                    <div class="rec-info">
                        <h4>Lisboa</h4>
                        <span class="loc">Portugal</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 2.800</strong>
                        </div>
                    </div>
                </a>
            </div>
        </div>
        `;
    } else {
        premiumContent = `
        <div style="text-align: center; margin-top: 50px; padding: 40px; background: var(--bg-secondary); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.1);">
            <h2 style="margin-bottom: 15px; color: var(--text-primary);">Desbloqueie todo o potencial do Partiu Viajar!</h2>
            <p style="color: var(--text-secondary); margin-bottom: 25px; max-width: 600px; margin-left: auto; margin-right: auto;">
                Como visitante, você pode fazer algumas buscas gratuitas. Ao criar sua conta gratuita, você terá acesso imediato a todas estas funcionalidades avançadas:
            </p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap;">
                <div style="background: var(--bg-main); padding: 15px 20px; border-radius: 8px;"><span class="icon">🔍</span> Buscas Ilimitadas</div>
                <div style="background: var(--bg-main); padding: 15px 20px; border-radius: 8px;"><span class="icon">❤️</span> Favoritos salvos</div>
                <div style="background: var(--bg-main); padding: 15px 20px; border-radius: 8px;"><span class="icon">🔔</span> Alertas de preço</div>
                <div style="background: var(--bg-main); padding: 15px 20px; border-radius: 8px;"><span class="icon">🕒</span> Histórico de buscas</div>
            </div>
            <button onclick="window.showAuthModal()" class="btn-magic" style="padding: 12px 30px; font-size: 1.1rem; border-radius: 25px; cursor: pointer;">Fazer Login / Cadastrar agora</button>
        </div>
        `;
    }

    container.innerHTML = `
        <h1 class="page-title">Meu Painel</h1>
        
        <!-- Welcome Banner -->
        <div class="welcome-banner">
            <div class="user-profile">
                <img src="${userAvatar}" alt="Avatar" class="avatar-huge">
                <div>
                    <h2>Olá, ${userName}! 👋</h2>
                    <p class="subtitle">Bem-vindo(a) ao Partiu Viajar</p>
                    <span class="badge">${memberSince}</span>
                </div>
            </div>
            ${token ? `
            <div class="level-info">
                <div class="level-header">
                    <span class="level-label">NÍVEL ATUAL</span>
                    <span class="level-title">Explorador ✈️</span>
                </div>
                <div class="progress-container">
                    <div class="progress-texts">
                        <span>0 pontos</span>
                        <span class="next-level">Próximo nível: 100 pontos</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            </div>` : ''}
        </div>

        ${premiumContent}
    `;

    setTimeout(() => {
        const mapEl = container.querySelector('#dashboard-map');
        if (mapEl) {
            if (mapEl._leaflet_id) { mapEl._leaflet_id = null; }
            if (window._dashboardMap) { window._dashboardMap.remove(); }
            
            const map = L.map(mapEl).setView([-14.235, -51.925], 4);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            L.marker([-3.7172, -38.5433]).addTo(map).bindPopup('Fortaleza, CE');
            L.marker([-23.5505, -46.6333]).addTo(map).bindPopup('São Paulo, SP');
            L.marker([-22.9068, -43.1729]).addTo(map).bindPopup('Rio de Janeiro, RJ');
            L.marker([-30.0346, -51.2177]).addTo(map).bindPopup('Porto Alegre, RS');
            L.marker([-8.5028, -34.9962]).addTo(map).bindPopup('Porto de Galinhas, PE');
            window._dashboardMap = map;
            
            // POI Layer and Fetch logic
            let poiLayer = L.layerGroup().addTo(map);
            let fetchTimeout = null;
            
            map.on('moveend', () => {
                if(map.getZoom() < 12) {
                    poiLayer.clearLayers();
                    return; 
                }
                
                clearTimeout(fetchTimeout);
                fetchTimeout = setTimeout(async () => {
                    const b = map.getBounds();
                    const query = `
                        [out:json][timeout:10];
                        (
                          node["tourism"~"hotel|guest_house|hostel"](${b.getSouth()},${b.getWest()},${b.getNorth()},${b.getEast()});
                          node["aeroway"~"aerodrome|terminal"](${b.getSouth()},${b.getWest()},${b.getNorth()},${b.getEast()});
                          node["amenity"~"bus_station"](${b.getSouth()},${b.getWest()},${b.getNorth()},${b.getEast()});
                        );
                        out body;
                    `;
                    try {
                        const resp = await fetch("https://overpass-api.de/api/interpreter", {
                            method: "POST",
                            body: "data=" + encodeURIComponent(query),
                            headers: { "Content-Type": "application/x-www-form-urlencoded" }
                        });
                        if (!resp.ok) return;
                        const data = await resp.json();
                        
                        poiLayer.clearLayers();
                        data.elements.forEach(el => {
                            if (!el.tags) return;
                            let icon = '📍', type = 'Local';
                            if (el.tags.aeroway) { icon = '✈️'; type = 'Aeroporto'; }
                            else if (el.tags.amenity === 'bus_station') { icon = '🚌'; type = 'Rodoviária'; }
                            else if (el.tags.tourism) { icon = '🏨'; type = 'Hospedagem'; }
                            
                            const name = el.tags.name || 'Desconhecido';
                            let actionHtml = '';
                            if (el.tags.tourism) {
                                const bookingUrl = `https://www.booking.com/searchresults.pt-br.html?aid=2336990&ss=${encodeURIComponent(name)}`;
                                actionHtml = `<div style="margin-top: 8px; text-align: center;"><a href="${bookingUrl}" target="_blank" style="display:inline-block; padding: 6px 10px; background: #004cb8; color: white; border-radius: 4px; text-decoration: none; font-size: 0.8rem; font-weight: bold; width: 100%;">Reservar no Booking</a></div>`;
                            } else if (el.tags.aeroway) {
                                actionHtml = `<div style="margin-top: 8px; text-align: center;"><a href="https://www.skyscanner.com.br/" target="_blank" style="display:inline-block; padding: 6px 10px; background: #0770e3; color: white; border-radius: 4px; text-decoration: none; font-size: 0.8rem; font-weight: bold; width: 100%;">Buscar Voos</a></div>`;
                            }
                            
                            const divIcon = L.divIcon({
                                html: `<div style="font-size: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">${icon}</div>`,
                                className: '',
                                iconSize: [20, 20], iconAnchor: [10, 20]
                            });
                            
                            L.marker([el.lat, el.lon], {icon: divIcon})
                                .bindPopup(`<div style="min-width: 150px;"><strong>${name}</strong><br><small style="color: #666;">${type}</small>${actionHtml}</div>`)
                                .addTo(poiLayer);
                        });
                    } catch(e) {}
                }, 1000);
            });
            
            setTimeout(() => { map.invalidateSize(); }, 300);
        }
    }, 150);

    return container;
}
