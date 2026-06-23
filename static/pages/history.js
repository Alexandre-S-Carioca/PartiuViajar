export function renderHistory() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <h1 class="page-title mb-15">Histórico de Buscas</h1>
        
        <div class="dashboard-panel">
            <div class="list-content">
                <div class="history-item">
                    <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.05); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">✈️</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">Fortaleza → São Paulo</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">Ida e Volta • 1 Adulto • Econômica</div>
                    </div>
                    <div style="text-align: right; margin-right: 16px;">
                        <div style="font-size: 0.85rem;">23/06/2026</div>
                    </div>
                    <button class="btn-outline" style="padding: 6px 12px; font-size: 0.8rem;">Pesquisar novamente</button>
                </div>
                <div class="history-item">
                    <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.05); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 12px;">🏨</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">Hotéis em Gramado</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">01/07 a 04/07 • 2 Adultos</div>
                    </div>
                    <div style="text-align: right; margin-right: 16px;">
                        <div style="font-size: 0.85rem;">21/06/2026</div>
                    </div>
                    <button class="btn-outline" style="padding: 6px 12px; font-size: 0.8rem;">Pesquisar novamente</button>
                </div>
            </div>
        </div>
    `;

    return container;
}
