export function renderPreferences() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <h1 class="page-title mb-15">Preferências</h1>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">Personalize sua experiência no Partiu Viajar.</p>

        <div class="dashboard-panel" style="max-width: 600px;">
            <div style="margin-bottom: 24px;">
                <h3 style="margin-bottom: 12px;">Companhias Favoritas</h3>
                <label style="display: block; margin-bottom: 8px;"><input type="checkbox" checked> LATAM</label>
                <label style="display: block; margin-bottom: 8px;"><input type="checkbox" checked> GOL</label>
                <label style="display: block; margin-bottom: 8px;"><input type="checkbox"> Azul</label>
            </div>

            <div style="margin-bottom: 24px;">
                <h3 style="margin-bottom: 12px;">Classe Padrão</h3>
                <select style="width: 100%; padding: 10px; border-radius: var(--border-radius-sm); background: var(--bg-main); color: var(--text-primary); border: 1px solid rgba(255,255,255,0.1);">
                    <option selected>Econômica</option>
                    <option>Executiva</option>
                </select>
            </div>

            <div style="margin-bottom: 24px;">
                <h3 style="margin-bottom: 12px;">Idioma e Moeda</h3>
                <div style="display: flex; gap: 16px;">
                    <select style="flex: 1; padding: 10px; border-radius: var(--border-radius-sm); background: var(--bg-main); color: var(--text-primary); border: 1px solid rgba(255,255,255,0.1);">
                        <option selected>Português (BR)</option>
                        <option>English</option>
                    </select>
                    <select style="flex: 1; padding: 10px; border-radius: var(--border-radius-sm); background: var(--bg-main); color: var(--text-primary); border: 1px solid rgba(255,255,255,0.1);">
                        <option selected>BRL (R$)</option>
                        <option>USD ($)</option>
                        <option>EUR (€)</option>
                    </select>
                </div>
            </div>

            <button class="btn-outline full-width" style="background: var(--primary); color: white; border: none;">Salvar Preferências</button>
        </div>
    `;

    return container;
}
