export function renderHistory() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <h1 class="page-title mb-15">Histórico de Buscas</h1>
        <div class="dashboard-panel">
            <div class="list-content" id="history-list">
                <!-- Skeletons -->
                <div class="history-item"><div class="skeleton skeleton-card" style="width: 100%; height: 60px;"></div></div>
                <div class="history-item"><div class="skeleton skeleton-card" style="width: 100%; height: 60px;"></div></div>
                <div class="history-item"><div class="skeleton skeleton-card" style="width: 100%; height: 60px;"></div></div>
            </div>
        </div>
    `;

    setTimeout(async () => {
        const list = container.querySelector('#history-list');
        try {
            const res = await fetch('/api/search-history');
            let data = [];
            if(res.ok) data = await res.json();
            
            // Mock Fallback
            if(data.length === 0) {
                data = [
                    { id: 1, origin: "Fortaleza", destination: "São Paulo", adults: 1, type: "✈️", date: "23/06/2026" },
                    { id: 2, origin: "Hotéis", destination: "Gramado", adults: 2, type: "🏨", date: "21/06/2026" }
                ];
            }

            list.innerHTML = data.map(item => `
                <div class="history-item">
                    <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.05); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">${item.type || '🔍'}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">${item.origin} ➔ ${item.destination}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">${item.adults} Adulto(s)</div>
                    </div>
                    <div style="text-align: right; margin-right: 16px;">
                        <div style="font-size: 0.85rem;">${item.date || item.departure_date || ''}</div>
                    </div>
                    <button class="btn-outline" style="padding: 6px 12px; font-size: 0.8rem;" onclick="window.showToast('Buscando novamente...', 'success')">Pesquisar novamente</button>
                </div>
            `).join('');
        } catch(e) {
            list.innerHTML = '<p style="text-align:center; padding: 20px;">Erro ao carregar histórico.</p>';
        }
    }, 800);

    return container;
}
