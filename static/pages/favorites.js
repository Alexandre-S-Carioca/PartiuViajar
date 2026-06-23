export function renderFavorites() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <h1 class="page-title mb-15">Meus Favoritos</h1>
        
        <div class="tabs-container mb-15">
            <button class="tab-btn active"><span class="icon">✈️</span> Passagens</button>
            <button class="tab-btn"><span class="icon">🏨</span> Hotéis</button>
            <button class="tab-btn"><span class="icon">📍</span> Destinos</button>
        </div>

        <div class="cards-carousel">
            <!-- Favorite 1 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=300&q=80" alt="Jericoacoara">
                <div class="rec-info">
                    <h4>Jericoacoara</h4>
                    <span class="loc">Brasil</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço encontrado</span>
                        <strong>R$ 850</strong>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-outline full-width" style="font-size: 0.8rem; padding: 8px;">Ver detalhes</button>
                        <button class="btn-outline" style="border-color: var(--danger); color: var(--danger); padding: 8px;">🗑️</button>
                    </div>
                </div>
            </div>
            
            <!-- Favorite 2 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1589909202802-8f4aadce1849?auto=format&fit=crop&w=300&q=80" alt="Buenos Aires">
                <div class="rec-info">
                    <h4>Buenos Aires</h4>
                    <span class="loc">Argentina</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço encontrado</span>
                        <strong>R$ 1.200</strong>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-outline full-width" style="font-size: 0.8rem; padding: 8px;">Ver detalhes</button>
                        <button class="btn-outline" style="border-color: var(--danger); color: var(--danger); padding: 8px;">🗑️</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    return container;
}
