export function renderTracker() {
    const container = document.createElement('div');
    container.className = 'tracker-page';

    container.innerHTML = `
        <h1 class="page-title">Rastreio em Tempo Real</h1>
        <p class="subtitle" style="margin-bottom: 30px; color: var(--text-secondary);">Acompanhe o status do seu voo diretamente no mapa global.</p>

        <div style="display: flex; flex-direction: row; gap: 30px; align-items: stretch; margin-top: 30px; width: 100%;">
            <!-- Coluna Esquerda -->
            <div style="width: 320px; min-width: 320px; flex-shrink: 0; display: flex; flex-direction: column; gap: 15px;">
                <div style="background: var(--bg-secondary); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; gap: 12px;">
                    <input type="text" id="flight-iata-input" placeholder="Ex: AZU4712" style="width: 100%; box-sizing: border-box; padding: 12px 15px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-primary); font-size: 1rem;" autocomplete="off">
                    <button id="btn-track-flight" class="btn-magic" style="width: 100%; padding: 12px 0; border-radius: 8px; font-weight: 600; cursor: pointer;">Localizar</button>
                </div>

                <div id="tracker-result-container" style="flex: 1; background: var(--bg-secondary); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; min-height: 300px;">
                    <!-- Estado Vazio -->
                    <div id="tracker-empty-state" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px 20px; text-align: center; color: var(--text-secondary); opacity: 0.6;">
                        <div style="font-size: 3.5rem; margin-bottom: 12px;">📡</div>
                        <p>Digite o código do voo acima para iniciar o rastreamento.</p>
                    </div>

                    <!-- Loader (escondido) -->
                    <div id="tracker-loader" class="hidden" style="display: none; flex: 1; flex-direction: column; align-items: center; justify-content: center; padding: 30px 20px;">
                        <div class="spinner" style="margin-bottom: 15px;"></div>
                        <p style="color: var(--text-secondary);">Buscando sinal do transponder...</p>
                    </div>

                    <!-- Cartão do Voo (escondido) -->
                    <div id="tracker-card" class="tracker-premium-card hidden" style="display: none; border: none; background: transparent; padding: 20px;">
                        <!-- Preenchido via JS -->
                    </div>
                </div>
            </div>

            <!-- Coluna Direita (Mapa) -->
            <div class="dashboard-panel" style="flex: 1; margin-top: 0; display: flex; flex-direction: column; min-width: 0;">
                <div class="panel-header">
                    <h3>Radar Global Ao Vivo</h3>
                    <button onclick="window.toggleTrackerMapFullscreen()" title="Tela Cheia" style="padding: 4px 8px; border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color); cursor: pointer; font-size: 1rem;">⛶</button>
                </div>
                <div style="padding: 0; flex: 1; display: flex; min-width: 0;">
                    <div id="tracker-live-map" style="width: 100%; min-height: 480px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;"></div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const btnTrack = container.querySelector('#btn-track-flight');
        const inputIata = container.querySelector('#flight-iata-input');
        
        btnTrack.addEventListener('click', () => performTracking(inputIata.value));
        inputIata.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') performTracking(inputIata.value);
        });

        const mapEl = container.querySelector('#tracker-live-map');
        if (mapEl) {
            if (mapEl._leaflet_id) { mapEl._leaflet_id = null; }
            if (window._trackerMap) { window._trackerMap.remove(); }
            if (window._trackerFlightsInterval) { clearInterval(window._trackerFlightsInterval); }
            
            const savedLat = localStorage.getItem('user_lat');
            const savedLon = localStorage.getItem('user_lon');
            let map;
            if (savedLat && savedLon) {
                map = L.map(mapEl).setView([parseFloat(savedLat), parseFloat(savedLon)], 6);
            } else {
                map = L.map(mapEl).setView([-14.235, -51.925], 4);
            }

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            window._trackerMap = map;
            
            let flightsLayer = L.layerGroup().addTo(map);
            let activeFlights = {}; 

            function updateFlights() {
                if (map.getZoom() < 3) {
                    flightsLayer.clearLayers();
                    activeFlights = {};
                    return;
                }
                const b = map.getBounds();
                fetch(`/api/v1/flights/live-radar?lamin=${b.getSouth()}&lamax=${b.getNorth()}&lomin=${b.getWest()}&lomax=${b.getEast()}`)
                    .then(r => r.json())
                    .then(flights => {
                        const newActive = {};
                        if (!Array.isArray(flights)) return;
                        flights.forEach(f => {
                            newActive[f.icao24] = true;
                            if (activeFlights[f.icao24]) {
                                const marker = activeFlights[f.icao24];
                                marker.setLatLng([f.latitude, f.longitude]);
                                const iconEl = marker.getElement();
                                if (iconEl) {
                                    const div = iconEl.querySelector('div');
                                    if (div) div.style.transform = `rotate(${f.true_track}deg)`;
                                }
                                marker.getPopup().setContent(`<strong>Voo: ${f.callsign}</strong><br>País: ${f.origin_country}<br>Altitude: ${Math.round(f.altitude)}m<br>Vel: ${Math.round(f.velocity * 3.6)} km/h`);
                            } else {
                                const divIcon = L.divIcon({
                                    html: `<div style="font-size: 24px; text-shadow: 0 0 5px #00e5ff; transform: rotate(${f.true_track}deg); transition: transform 1s, left 1s, top 1s;">✈️</div>`,
                                    className: '',
                                    iconSize: [24, 24], iconAnchor: [12, 12]
                                });
                                const marker = L.marker([f.latitude, f.longitude], {icon: divIcon})
                                    .bindPopup(`<strong>Voo: ${f.callsign}</strong><br>País: ${f.origin_country}<br>Altitude: ${Math.round(f.altitude)}m<br>Vel: ${Math.round(f.velocity * 3.6)} km/h`)
                                    .addTo(flightsLayer);
                                activeFlights[f.icao24] = marker;
                            }
                        });
                        Object.keys(activeFlights).forEach(id => {
                            if (!newActive[id]) {
                                flightsLayer.removeLayer(activeFlights[id]);
                                delete activeFlights[id];
                            }
                        });
                    }).catch(e => console.error("Error fetching flights:", e));
            }
            window._trackerFlightsInterval = setInterval(updateFlights, 20000);
            
            map.on('moveend', () => {
                updateFlights();
            });
            setTimeout(() => { map.invalidateSize(); updateFlights(); }, 300);
            
            window.toggleTrackerMapFullscreen = function() {
                if (!document.fullscreenElement) {
                    mapEl.requestFullscreen().catch(err => {
                        console.error(`Error attempting to enable fullscreen: ${err.message}`);
                    });
                } else {
                    document.exitFullscreen();
                }
            };
        }

    }, 100);

    return container;
}

async function performTracking(iata) {
    iata = iata.trim().toUpperCase();
    if(!iata) return;

    const emptyState = document.getElementById('tracker-empty-state');
    const loader = document.getElementById('tracker-loader');
    const card = document.getElementById('tracker-card');

    if(emptyState) emptyState.style.display = 'none';
    if(card) card.style.display = 'none';
    if(loader) loader.style.display = 'flex';

    try {
        const response = await fetch(`/api/v1/flights/live/${iata}`);
        if(!response.ok) {
            throw new Error('Voo não encontrado ou sem sinal GPS ativo.');
        }
        
        const data = await response.json();
        renderFlightCard(data);
    } catch(err) {
        window.showToast(err.message, 'error');
        if(emptyState) emptyState.style.display = 'flex';
    } finally {
        if(loader) loader.style.display = 'none';
    }
}

function renderFlightCard(data) {
    const card = document.getElementById('tracker-card');
    if(!card) return;

    const statusMap = {
        'active': { label: 'EM VOO', color: '#10B981' },
        'scheduled': { label: 'AGENDADO', color: '#3B82F6' },
        'landed': { label: 'POUSOU', color: '#6B7280' },
        'cancelled': { label: 'CANCELADO', color: '#EF4444' },
        'incident': { label: 'INCIDENTE', color: '#F59E0B' },
        'diverted': { label: 'DESVIADO', color: '#F59E0B' }
    };

    const statusInfo = statusMap[data.flight_status] || { label: data.flight_status.toUpperCase(), color: '#888' };
    
    // Calcula progresso fake visual se estiver "active"
    let progressWidth = '0%';
    if(data.flight_status === 'active') progressWidth = '50%';
    if(data.flight_status === 'landed') progressWidth = '100%';

    const formatTime = (timeStr) => {
        if(!timeStr) return '--:--';
        const d = new Date(timeStr);
        return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute:'2-digit' });
    };

    card.innerHTML = `
        <div class="tracker-header">
            <div class="airline-info">
                <span class="airline-name">${data.airline_name || 'Companhia Aérea'}</span>
                <span class="flight-number">${data.flight_iata || data.flight_number}</span>
            </div>
            <div class="status-badge" style="background: ${statusInfo.color}20; color: ${statusInfo.color}; border: 1px solid ${statusInfo.color}50; box-shadow: 0 0 10px ${statusInfo.color}30;">
                <span class="status-dot" style="background: ${statusInfo.color}; box-shadow: 0 0 8px ${statusInfo.color};"></span>
                ${statusInfo.label}
            </div>
        </div>

        <div class="tracker-route-container">
            <div class="airport-block text-left">
                <div class="iata-code">${data.departure_iata || '---'}</div>
                <div class="airport-name">${data.departure_airport || 'Aeroporto de Origem'}</div>
                <div class="time-sched">Previsto: ${formatTime(data.departure_scheduled)}</div>
                ${data.departure_actual ? `<div class="time-actual">Partida: ${formatTime(data.departure_actual)}</div>` : ''}
            </div>

            <div class="flight-progress-block">
                <div class="progress-track">
                    <div class="progress-fill" style="width: ${progressWidth}; background: ${statusInfo.color};"></div>
                    <div class="plane-icon" style="left: ${progressWidth}; color: ${statusInfo.color};">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                        </svg>
                    </div>
                </div>
                <div class="progress-label">${data.flight_date || ''}</div>
            </div>

            <div class="airport-block text-right">
                <div class="iata-code">${data.arrival_iata || '---'}</div>
                <div class="airport-name">${data.arrival_airport || 'Aeroporto de Destino'}</div>
                <div class="time-sched">Previsto: ${formatTime(data.arrival_scheduled)}</div>
                ${data.arrival_delay ? `<div class="delay-warning" style="color: #F59E0B; font-size: 0.85rem; margin-top: 4px;">Atraso: ${data.arrival_delay} min</div>` : ''}
            </div>
        </div>
    `;

    card.style.display = 'block';
}
