export function renderRestaurants() {
    const container = document.createElement('div');
    container.className = 'restaurants-page';

    container.innerHTML = `
        <h1 class="page-title">🍽️ Restaurantes</h1>
        <p class="subtitle" style="margin-bottom: 30px; color: var(--text-secondary);">Descubra os melhores restaurantes avaliados no TripAdvisor perto do seu destino.</p>

        <!-- Search Bar -->
        <div style="background: var(--bg-secondary); padding: 20px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.05); display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 30px;">
            <input type="text" id="restaurant-city-input" placeholder="🔍  Buscar cidade... (ex: Fortaleza)" 
                style="flex: 1; min-width: 200px; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-primary); font-size: 1rem;">
            <button id="btn-search-restaurants" class="btn-magic" style="padding: 12px 28px; border-radius: 10px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                Buscar Restaurantes
            </button>
            <button id="btn-nearby-restaurants" style="padding: 12px 20px; border-radius: 10px; font-weight: 600; cursor: pointer; white-space: nowrap; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary);">
                📍 Perto de Mim
            </button>
        </div>

        <!-- Results Area -->
        <div id="restaurants-result-area">
            <!-- Empty State -->
            <div id="restaurants-empty" style="text-align: center; padding: 80px 20px; color: var(--text-secondary); opacity: 0.5;">
                <div style="font-size: 5rem; margin-bottom: 20px;">🍽️</div>
                <p style="font-size: 1.1rem;">Busque uma cidade para descobrir os melhores restaurantes.</p>
            </div>

            <!-- Loader -->
            <div id="restaurants-loader" style="display: none; text-align: center; padding: 60px 20px;">
                <div class="spinner" style="margin: 0 auto 20px;"></div>
                <p style="color: var(--text-secondary);">Buscando restaurantes no TripAdvisor...</p>
            </div>

            <!-- Cards Grid -->
            <div id="restaurants-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; display: none;"></div>
        </div>
    `;

    setTimeout(() => {
        const cityInput = document.getElementById('restaurant-city-input');
        const searchBtn = document.getElementById('btn-search-restaurants');
        const nearbyBtn = document.getElementById('btn-nearby-restaurants');

        const LOCATION_IDS = {
            'fortaleza': 304554,
            'são paulo': 303631,
            'sao paulo': 303631,
            'rio de janeiro': 303506,
            'rio': 303506,
            'brasília': 303451,
            'brasilia': 303451,
            'salvador': 303588,
            'recife': 303568,
            'manaus': 303536,
            'curitiba': 303461,
            'belo horizonte': 303413,
            'porto alegre': 303563,
            'natal': 303543,
            'florianópolis': 303499,
            'florianopolis': 303499,
        };

        async function searchByCity(city) {
            const key = city.trim().toLowerCase();
            const locationId = LOCATION_IDS[key];
            showLoader();
            try {
                let url = locationId
                    ? `/api/v1/restaurants?location_id=${locationId}&limit=20`
                    : `/api/v1/restaurants?location_id=304554&limit=20`; // fallback Fortaleza
                const res = await fetch(url);
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    renderCards(data, city);
                } else {
                    showError('Nenhum restaurante encontrado para esta cidade. Tente outra.');
                }
            } catch (e) {
                showError('Erro ao buscar restaurantes. Tente novamente.');
            }
        }

        async function searchNearby() {
            showLoader();
            const saved = localStorage.getItem('userLat');
            if (!saved) {
                navigator.geolocation.getCurrentPosition(async (pos) => {
                    const { latitude: lat, longitude: lon } = pos.coords;
                    await fetchByGeo(lat, lon);
                }, () => showError('Não foi possível obter sua localização.'));
            } else {
                const lat = parseFloat(localStorage.getItem('userLat'));
                const lon = parseFloat(localStorage.getItem('userLon'));
                await fetchByGeo(lat, lon);
            }
        }

        async function fetchByGeo(lat, lon) {
            try {
                const res = await fetch(`/api/v1/restaurants?lat=${lat}&lon=${lon}&limit=20`);
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    renderCards(data, 'Perto de Você');
                } else {
                    showError('Nenhum restaurante encontrado perto de você.');
                }
            } catch (e) {
                showError('Erro ao buscar restaurantes próximos.');
            }
        }

        function showLoader() {
            document.getElementById('restaurants-empty').style.display = 'none';
            document.getElementById('restaurants-loader').style.display = 'block';
            document.getElementById('restaurants-grid').style.display = 'none';
        }

        function showError(msg) {
            document.getElementById('restaurants-loader').style.display = 'none';
            document.getElementById('restaurants-grid').style.display = 'none';
            const empty = document.getElementById('restaurants-empty');
            empty.style.display = 'block';
            empty.innerHTML = `<div style="font-size: 4rem; margin-bottom: 15px;">⚠️</div><p>${msg}</p>`;
        }

        function renderCards(restaurants, title) {
            document.getElementById('restaurants-loader').style.display = 'none';
            document.getElementById('restaurants-empty').style.display = 'none';
            const grid = document.getElementById('restaurants-grid');
            grid.style.display = 'grid';

            grid.innerHTML = `<div style="grid-column: 1/-1; margin-bottom: 10px;">
                <h3 style="font-size: 1.1rem; color: var(--text-secondary);">
                    ${restaurants.length} restaurantes encontrados em <strong style="color: var(--text-primary);">${title}</strong>
                </h3>
            </div>` + restaurants.map(r => buildCard(r)).join('');
        }

        function buildCard(r) {
            const stars = r.rating ? renderStars(r.rating) : '';
            const photo = r.photo
                ? `<img src="${r.photo}" alt="${r.name}" style="width:100%; height:160px; object-fit:cover;" onerror="this.style.display='none'">`
                : `<div style="width:100%; height:160px; background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card)); display:flex; align-items:center; justify-content:center; font-size:3rem;">🍽️</div>`;

            return `
                <div style="background: var(--bg-card); border-radius: 14px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); transition: transform 0.3s, box-shadow 0.3s;" 
                     onmouseenter="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.4)'"
                     onmouseleave="this.style.transform=''; this.style.boxShadow=''">
                    ${photo}
                    <div style="padding: 16px;">
                        <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 6px; line-height: 1.3;">${r.name}</h4>
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; flex-wrap: wrap;">
                            ${stars ? `<span style="color: #F59E0B; font-size:0.85rem;">${stars}</span>` : ''}
                            ${r.rating ? `<span style="color: var(--text-secondary); font-size: 0.8rem;">${r.rating} (${r.reviews?.toLocaleString('pt-BR') || 0} avaliações)</span>` : ''}
                        </div>
                        <div style="display:flex; gap:8px; flex-wrap: wrap; margin-bottom:10px;">
                            ${r.cuisines ? `<span style="font-size:0.75rem; padding: 3px 10px; border-radius: 20px; background: rgba(6,182,212,0.1); color: var(--primary); border: 1px solid rgba(6,182,212,0.2);">${r.cuisines}</span>` : ''}
                            ${r.price_level ? `<span style="font-size:0.75rem; padding: 3px 10px; border-radius: 20px; background: rgba(255,255,255,0.05); color: var(--text-secondary);">${r.price_level}</span>` : ''}
                        </div>
                        ${r.address ? `<p style="font-size:0.8rem; color: var(--text-secondary); margin-bottom:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">📍 ${r.address}</p>` : ''}
                        <a href="${r.url}" target="_blank" rel="noopener"
                           style="display:block; text-align:center; padding: 9px; border-radius: 8px; background: var(--primary); color: #fff; font-weight: 600; font-size: 0.85rem; text-decoration: none; transition: background 0.2s;"
                           onmouseenter="this.style.background='#0891B2'" onmouseleave="this.style.background='var(--primary)'">
                            Ver no TripAdvisor ↗
                        </a>
                    </div>
                </div>`;
        }

        function renderStars(rating) {
            const full = Math.floor(rating);
            const half = rating % 1 >= 0.5 ? 1 : 0;
            return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - half);
        }

        searchBtn.addEventListener('click', () => {
            const city = cityInput.value.trim();
            if (city) searchByCity(city);
        });

        cityInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') searchBtn.click();
        });

        nearbyBtn.addEventListener('click', searchNearby);
    }, 100);

    return container;
}
