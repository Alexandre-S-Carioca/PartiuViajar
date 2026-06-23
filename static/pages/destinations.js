export function renderDestinations() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <h1 class="page-title mb-15">Destinos Salvos</h1>
        
        <div class="cards-carousel">
            <!-- Destination 1 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=300&q=80" alt="Jericoacoara">
                <div class="rec-info">
                    <h4>Jericoacoara</h4>
                    <span class="loc">Brasil</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço médio encontrado</span>
                        <strong>R$ 850</strong>
                    </div>
                    <button class="btn-outline full-width">Pesquisar agora</button>
                </div>
            </div>
            
            <!-- Destination 2 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1632709230588-46dae858dbab?auto=format&fit=crop&w=300&q=80" alt="Gramado">
                <div class="rec-info">
                    <h4>Gramado</h4>
                    <span class="loc">Brasil</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço médio encontrado</span>
                        <strong>R$ 1.100</strong>
                    </div>
                    <button class="btn-outline full-width">Pesquisar agora</button>
                </div>
            </div>
            
            <!-- Destination 3 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1585208798174-6cedd86e019a?auto=format&fit=crop&w=300&q=80" alt="Lisboa">
                <div class="rec-info">
                    <h4>Lisboa</h4>
                    <span class="loc">Portugal</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço médio encontrado</span>
                        <strong>R$ 2.800</strong>
                    </div>
                    <button class="btn-outline full-width">Pesquisar agora</button>
                </div>
            </div>

            <!-- Destination 4 -->
            <div class="rec-card">
                <img src="https://images.unsplash.com/photo-1589909202802-8f4aadce1849?auto=format&fit=crop&w=300&q=80" alt="Buenos Aires">
                <div class="rec-info">
                    <h4>Buenos Aires</h4>
                    <span class="loc">Argentina</span>
                    <div class="rec-price mb-15">
                        <span class="from">Preço médio encontrado</span>
                        <strong>R$ 1.200</strong>
                    </div>
                    <button class="btn-outline full-width">Pesquisar agora</button>
                </div>
            </div>
        </div>
    `;

    return container;
}
