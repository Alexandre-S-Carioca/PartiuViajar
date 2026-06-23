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

        <div class="cards-carousel" id="favorites-list">
            <!-- Skeletons -->
            <div class="rec-card skeleton-card"></div>
            <div class="rec-card skeleton-card"></div>
            <div class="rec-card skeleton-card"></div>
        </div>
    `;

    setTimeout(async () => {
        const list = container.querySelector('#favorites-list');
        try {
            const res = await fetch('/api/favorites');
            let data = [];
            if(res.ok) data = await res.json();
            
            // Mock Fallback
            if(data.length === 0) {
                data = [
                    { id: 1, name: "Jericoacoara", location: "Brasil", price: 850, img: "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=300&q=80" },
                    { id: 2, name: "Buenos Aires", location: "Argentina", price: 1200, img: "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?auto=format&fit=crop&w=300&q=80" }
                ];
            }

            list.innerHTML = data.map(item => `
                <div class="rec-card">
                    <img src="${item.img}" alt="${item.name}">
                    <div class="rec-info">
                        <h4>${item.name}</h4>
                        <span class="loc">${item.location}</span>
                        <div class="rec-price mb-15">
                            <span class="from">Preço encontrado</span>
                            <strong>R$ ${item.price}</strong>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn-outline full-width" style="font-size: 0.8rem; padding: 8px;">Ver detalhes</button>
                            <button class="btn-outline" style="border-color: var(--danger); color: var(--danger); padding: 8px;" onclick="window.showToast('Removido dos favoritos', 'success')">🗑️</button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch(e) {
            list.innerHTML = '<p>Erro ao carregar favoritos.</p>';
        }
    }, 800);

    return container;
}
