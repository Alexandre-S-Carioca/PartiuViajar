export function renderAlerts() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 class="page-title">Alertas de Preço</h1>
            <button class="btn-outline" style="background: var(--primary); color: white; border: none;" onclick="window.showToast('Funcionalidade em desenvolvimento')">+ Novo Alerta</button>
        </div>
        
        <div class="dashboard-panel" style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-secondary);">
                        <th style="padding: 12px;">Origem</th>
                        <th style="padding: 12px;">Destino</th>
                        <th style="padding: 12px;">Preço desejado</th>
                        <th style="padding: 12px;">E-mail</th>
                        <th style="padding: 12px;">Status</th>
                        <th style="padding: 12px; text-align: right;">Ações</th>
                    </tr>
                </thead>
                <tbody id="alerts-tbody">
                    <!-- Skeletons -->
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                        <td style="padding: 16px 12px;"><div class="skeleton skeleton-text"></div></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Chart Modal -->
        <div class="modal-overlay" id="chart-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Evolução de Preço (Últimos 30 dias)</h3>
                    <button class="modal-close" id="close-chart-modal">×</button>
                </div>
                <canvas id="priceChart" width="400" height="150"></canvas>
            </div>
        </div>
    `;

    // Fetch data
    setTimeout(async () => {
        const tbody = container.querySelector('#alerts-tbody');
        try {
            // To simulate fetch if endpoint empty, we just do a mock if it fails
            const res = await fetch('/api/v1/flights/alerts');
            let data = [];
            if(res.ok) data = await res.json();
            
            // Mock fallback
            if(data.length === 0) {
                data = [
                    { origin: "FOR", destination: "GRU", target_price: 350.00, email: "user@email.com", is_active: true },
                    { origin: "FOR", destination: "LIS", target_price: 2800.00, email: "user@email.com", is_active: true }
                ];
            }

            tbody.innerHTML = data.map(item => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding: 16px 12px;">${item.origin}</td>
                    <td style="padding: 16px 12px; font-weight: 600;">${item.destination}</td>
                    <td style="padding: 16px 12px; color: var(--success); font-weight: 600;">R$ ${item.target_price.toFixed(2)}</td>
                    <td style="padding: 16px 12px; color: var(--text-secondary);">${item.email}</td>
                    <td style="padding: 16px 12px;">
                        <span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">
                            ${item.is_active ? 'Ativo' : 'Inativo'}
                        </span>
                    </td>
                    <td style="padding: 16px 12px; text-align: right; display: flex; gap: 8px; justify-content: flex-end;">
                        <button class="icon-btn-small" title="Ver Histórico de Preços" onclick="window.openChartModal()">📈</button>
                        <button class="icon-btn-small" title="Pausar">⏸️</button>
                        <button class="icon-btn-small" style="color: var(--danger);" title="Excluir" onclick="window.showToast('Alerta removido!', 'success')">🗑️</button>
                    </td>
                </tr>
            `).join('');
        } catch(e) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 20px; text-align: center;">Erro ao carregar dados.</td></tr>';
        }
    }, 800); // Artificial delay to show skeleton

    // Expose chart open globally for inline handlers
    window.openChartModal = () => {
        document.getElementById('chart-modal').classList.add('show');
        renderChart();
    };

    container.querySelector('#close-chart-modal').addEventListener('click', () => {
        document.getElementById('chart-modal').classList.remove('show');
    });

    return container;
}

let priceChartInstance = null;
function renderChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    if(priceChartInstance) priceChartInstance.destroy();
    
    // Mock 30 days data
    const labels = Array.from({length: 30}, (_, i) => `Dia ${i+1}`);
    const data = Array.from({length: 30}, () => Math.floor(Math.random() * (600 - 350 + 1) + 350));

    priceChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Preço (R$)',
                data: data,
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: false, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}
