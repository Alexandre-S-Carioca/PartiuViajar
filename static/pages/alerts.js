export function renderAlerts() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 class="page-title">Alertas de Preço</h1>
            <button class="btn-outline" style="background: var(--primary); color: white; border: none;" onclick="window.openAlertModal()">+ Novo Alerta</button>
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

        <!-- Create Alert Modal -->
        <style>
            .premium-modal .modal-content {
                background: linear-gradient(145deg, var(--bg-card) 0%, rgba(30, 41, 59, 0.9) 100%);
                border: 1px solid rgba(139, 92, 246, 0.3);
                box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
                border-radius: 16px;
                max-height: 90vh;
                overflow-y: auto;
                margin: auto; /* Garante que fique centralizado sem cortar no topo */
            }
            .premium-modal .modal-header h3 {
                background: linear-gradient(90deg, #A78BFA, #60A5FA);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700;
                font-size: 1.4rem;
            }
            .input-group-premium {
                position: relative;
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            .input-group-premium label {
                font-size: 0.8rem;
                color: var(--text-secondary);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .premium-input {
                background: rgba(0,0,0,0.2) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                padding: 14px 16px !important;
                border-radius: 12px !important;
                color: white !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
            }
            .premium-input:focus {
                border-color: #8B5CF6 !important;
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
                outline: none !important;
            }
            .premium-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
        </style>
        <div class="modal-overlay premium-modal" id="create-alert-modal">
            <div class="modal-content" style="max-width: 550px;">
                <div class="modal-header" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px; margin-bottom: 20px;">
                    <h3>✨ Criar Novo Alerta de Preço</h3>
                    <button class="modal-close" id="close-alert-modal">×</button>
                </div>
                <form id="create-alert-form" style="display: flex; flex-direction: column; gap: 20px;">
                    <div class="premium-grid">
                        <div class="input-group-premium" style="position: relative;">
                            <label>✈️ Origem</label>
                            <input type="text" id="alert-origin" class="search-input premium-input" placeholder="Ex: FOR" required autocomplete="off">
                            <div class="autocomplete-dropdown" id="alert-origin-autocomplete"></div>
                        </div>
                        <div class="input-group-premium" style="position: relative;">
                            <label>🛬 Destino</label>
                            <input type="text" id="alert-dest" class="search-input premium-input" placeholder="Ex: CGH" required autocomplete="off">
                            <div class="autocomplete-dropdown" id="alert-dest-autocomplete"></div>
                        </div>
                    </div>
                    
                    <div class="premium-grid">
                        <div class="input-group-premium">
                            <label>📅 Data do Voo</label>
                            <input type="date" id="alert-date" class="search-input premium-input" required>
                        </div>
                        <div class="input-group-premium">
                            <label>💰 Preço Alvo (Máximo)</label>
                            <input type="number" id="alert-price" class="search-input premium-input" placeholder="R$ 0,00" required step="0.01" min="1">
                        </div>
                    </div>

                    <div class="input-group-premium">
                        <label>✉️ E-mail para Notificação</label>
                        <input type="email" id="alert-email" class="search-input premium-input" placeholder="seu@email.com" required>
                    </div>
                    
                    <div class="input-group-premium">
                        <label>📱 Telegram Chat ID (Opcional)</label>
                        <input type="text" id="alert-telegram" class="search-input premium-input" placeholder="ID numérico do Telegram">
                    </div>

                    <button type="submit" class="btn-magic" style="margin-top: 10px; padding: 16px; font-size: 1.1rem; border-radius: 12px;">
                        Ativar Monitoramento Mágico 🪄
                    </button>
                </form>
            </div>
        </div>
    `;

    const loadAlerts = async () => {
        const tbody = container.querySelector('#alerts-tbody');
        try {
            const res = await fetch('/api/v1/flights/alerts');
            let data = [];
            if(res.ok) data = await res.json();
            
            if(data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="padding: 20px; text-align: center; color: var(--text-secondary);">Nenhum alerta cadastrado.</td></tr>';
                return;
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
                        <button class="icon-btn-small" style="color: var(--danger);" title="Excluir" onclick="window.deleteAlert(${item.id})">🗑️</button>
                    </td>
                </tr>
            `).join('');
        } catch(e) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 20px; text-align: center;">Erro ao carregar alertas.</td></tr>';
        }
    };

    setTimeout(() => {
        loadAlerts();
        if (window.setupAutocompleteForInput) {
            window.setupAutocompleteForInput('alert-origin', 'alert-origin-autocomplete');
            window.setupAutocompleteForInput('alert-dest', 'alert-dest-autocomplete');
        }
    }, 500); // Artificial delay to show skeleton

    // Expose functions globally for inline handlers
    window.openChartModal = () => {
        document.getElementById('chart-modal').classList.add('show');
        renderChart();
    };

    window.openAlertModal = () => {
        document.getElementById('create-alert-modal').classList.add('show');
    };

    window.deleteAlert = async (id) => {
        if(confirm("Tem certeza que deseja apagar este alerta?")) {
            try {
                const res = await fetch(`/api/v1/flights/alerts/${id}`, { method: 'DELETE' });
                if(res.ok) {
                    window.showToast('Alerta removido!', 'success');
                    loadAlerts();
                } else {
                    window.showToast('Erro ao remover alerta', 'error');
                }
            } catch(e) {
                window.showToast('Erro na conexão', 'error');
            }
        }
    };

    container.querySelector('#close-chart-modal').addEventListener('click', () => {
        document.getElementById('chart-modal').classList.remove('show');
    });

    container.querySelector('#close-alert-modal').addEventListener('click', () => {
        document.getElementById('create-alert-modal').classList.remove('show');
    });

    container.querySelector('#create-alert-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const originVal = document.getElementById('alert-origin').value;
        const destVal = document.getElementById('alert-dest').value;
        
        // Extract IATA code from "City (IATA)" format or use raw value
        const extractIata = (str) => {
            const match = str.match(/\(([A-Z]{3})\)/);
            return match ? match[1] : str.substring(0,3).toUpperCase();
        };

        const payload = {
            origin: extractIata(originVal),
            destination: extractIata(destVal),
            departure_date: document.getElementById('alert-date').value,
            target_price: parseFloat(document.getElementById('alert-price').value),
            email: document.getElementById('alert-email').value,
            telegram_chat_id: document.getElementById('alert-telegram').value
        };

        const btn = e.target.querySelector('button');
        btn.disabled = true;
        btn.textContent = "Salvando...";

        try {
            const res = await fetch('/api/v1/flights/alerts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if(res.ok) {
                window.showToast('Alerta criado com sucesso!', 'success');
                document.getElementById('create-alert-modal').classList.remove('show');
                e.target.reset();
                loadAlerts();
            } else {
                const err = await res.json();
                let errMsg = 'Erro ao criar alerta';
                if (err.detail) {
                    if (Array.isArray(err.detail)) {
                        errMsg = err.detail.map(e => e.msg || 'Erro de validação').join(', ');
                    } else {
                        errMsg = err.detail;
                    }
                }
                window.showToast(errMsg, 'error');
            }
        } catch(err) {
            window.showToast('Erro de conexão', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = "Salvar Alerta";
        }
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
