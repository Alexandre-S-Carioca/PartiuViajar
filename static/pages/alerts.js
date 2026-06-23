export function renderAlerts() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 class="page-title">Alertas de Preço</h1>
            <button class="btn-outline" style="background: var(--primary); color: white; border: none;">+ Novo Alerta</button>
        </div>
        
        <div class="dashboard-panel" style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-secondary);">
                        <th style="padding: 12px;">Origem</th>
                        <th style="padding: 12px;">Destino</th>
                        <th style="padding: 12px;">Preço atual</th>
                        <th style="padding: 12px;">Preço desejado</th>
                        <th style="padding: 12px;">Status</th>
                        <th style="padding: 12px; text-align: right;">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 16px 12px;">Fortaleza (FOR)</td>
                        <td style="padding: 16px 12px; font-weight: 600;">São Paulo (GRU)</td>
                        <td style="padding: 16px 12px;">R$ 480</td>
                        <td style="padding: 16px 12px; color: var(--success); font-weight: 600;">R$ 350</td>
                        <td style="padding: 16px 12px;"><span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">Ativo</span></td>
                        <td style="padding: 16px 12px; text-align: right; display: flex; gap: 8px; justify-content: flex-end;">
                            <button class="icon-btn-small">✏️</button>
                            <button class="icon-btn-small">⏸️</button>
                            <button class="icon-btn-small" style="color: var(--danger);">🗑️</button>
                        </td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 16px 12px;">Fortaleza (FOR)</td>
                        <td style="padding: 16px 12px; font-weight: 600;">Lisboa (LIS)</td>
                        <td style="padding: 16px 12px;">R$ 3.200</td>
                        <td style="padding: 16px 12px; color: var(--success); font-weight: 600;">R$ 2.800</td>
                        <td style="padding: 16px 12px;"><span class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success);">Ativo</span></td>
                        <td style="padding: 16px 12px; text-align: right; display: flex; gap: 8px; justify-content: flex-end;">
                            <button class="icon-btn-small">✏️</button>
                            <button class="icon-btn-small">⏸️</button>
                            <button class="icon-btn-small" style="color: var(--danger);">🗑️</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;

    return container;
}
