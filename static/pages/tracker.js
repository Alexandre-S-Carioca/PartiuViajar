export function renderTracker() {
    const container = document.createElement('div');
    container.className = 'dashboard-container tracker-page';

    container.innerHTML = `
        <h1 class="page-title">Rastreio em Tempo Real</h1>
        <p class="subtitle" style="margin-bottom: 30px; color: var(--text-secondary);">Acompanhe o status do seu voo diretamente no mapa global.</p>

        <div class="tracker-search-box" style="margin-bottom: 40px; background: var(--bg-secondary); padding: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); display: flex; gap: 10px; max-width: 500px;">
            <input type="text" id="flight-iata-input" placeholder="Ex: 3U9619" style="flex: 1; padding: 12px 15px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-primary); font-size: 1rem;" autocomplete="off">
            <button id="btn-track-flight" class="btn-magic" style="padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">Localizar</button>
        </div>

        <div id="tracker-result-container" style="min-height: 300px;">
            <!-- Estado Vazio -->
            <div id="tracker-empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 50px; text-align: center; color: var(--text-secondary); opacity: 0.6;">
                <div style="font-size: 4rem; margin-bottom: 15px;">📡</div>
                <p>Digite o código do voo acima para iniciar o rastreamento.</p>
            </div>

            <!-- Loader (escondido) -->
            <div id="tracker-loader" class="hidden" style="display: none; flex-direction: column; align-items: center; justify-content: center; padding: 50px;">
                <div class="spinner" style="margin-bottom: 15px;"></div>
                <p style="color: var(--text-secondary);">Buscando sinal do transponder...</p>
            </div>

            <!-- Cartão do Voo (escondido) -->
            <div id="tracker-card" class="tracker-premium-card hidden" style="display: none;">
                <!-- Preenchido via JS -->
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
