export function renderDashboard() {
    const container = document.createElement('div');
    container.className = 'dashboard-container';

    container.innerHTML = `
        <h1 class="page-title">Meu Painel</h1>
        
        <!-- Welcome Banner -->
        <div class="welcome-banner">
            <div class="user-profile">
                <img src="https://ui-avatars.com/api/?name=Alexandre&background=0D8ABC&color=fff&size=80" alt="Avatar" class="avatar-huge">
                <div>
                    <h2>Olá, Alexandre! 👋</h2>
                    <p class="subtitle">Bem-vindo de volta ao Partiu Viajar</p>
                    <span class="badge">Membro desde Junho/2026</span>
                </div>
            </div>
            <div class="level-info">
                <div class="level-header">
                    <span class="level-label">NÍVEL ATUAL</span>
                    <span class="level-title">Explorador ✈️</span>
                </div>
                <div class="progress-container">
                    <div class="progress-texts">
                        <span>120 pontos</span>
                        <span class="next-level">Próximo nível: 380 pontos</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 24%"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card" style="--bg: var(--card-search-bg); --icon-color: var(--card-search-icon)">
                <div class="icon-box">🔍</div>
                <div class="stat-info">
                    <h3>48</h3>
                    <p>Pesquisas realizadas</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-fav-bg); --icon-color: var(--card-fav-icon)">
                <div class="icon-box">❤️</div>
                <div class="stat-info">
                    <h3>12</h3>
                    <p>Favoritos salvos</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-alert-bg); --icon-color: var(--card-alert-icon)">
                <div class="icon-box">🔔</div>
                <div class="stat-info">
                    <h3>5</h3>
                    <p>Alertas ativos de preço</p>
                </div>
            </div>
            <div class="stat-card" style="--bg: var(--card-dest-bg); --icon-color: var(--card-dest-icon)">
                <div class="icon-box">📍</div>
                <div class="stat-info">
                    <h3>8</h3>
                    <p>Destinos salvos</p>
                </div>
            </div>
        </div>

        <!-- 3 Columns Layout -->
        <div class="three-cols-grid">
            <!-- Price Alerts -->
            <div class="dashboard-panel">
                <div class="panel-header">
                    <h3>Alertas de preço ativos</h3>
                    <a href="#/alerts" class="link-btn">Ver todos</a>
                </div>
                <div class="panel-content">
                    <div class="alert-item">
                        <div class="alert-icon">✈️</div>
                        <div class="alert-details">
                            <span class="route">Fortaleza → São Paulo</span>
                            <div class="prices">
                                <div class="price-box"><span>Preço atual</span><strong>R$ 480</strong></div>
                                <div class="price-box target"><span>Meta</span><strong>R$ 350</strong></div>
                            </div>
                        </div>
                        <button class="icon-btn-small">🔔</button>
                    </div>
                    <div class="alert-item">
                        <div class="alert-icon">✈️</div>
                        <div class="alert-details">
                            <span class="route">Fortaleza → Lisboa</span>
                            <div class="prices">
                                <div class="price-box"><span>Preço atual</span><strong>R$ 3.200</strong></div>
                                <div class="price-box target"><span>Meta</span><strong>R$ 2.800</strong></div>
                            </div>
                        </div>
                        <button class="icon-btn-small">🔔</button>
                    </div>
                    <button class="btn-outline full-width mt-10">Gerenciar alertas</button>
                </div>
            </div>

            <!-- Recent Searches -->
            <div class="dashboard-panel">
                <div class="panel-header">
                    <h3>Últimas buscas</h3>
                    <a href="#/history" class="link-btn">Ver histórico</a>
                </div>
                <div class="panel-content list-content">
                    <div class="history-item">
                        <span class="icon">🕒</span> <span class="text">Fortaleza → São Paulo</span> <span class="date">23/06/2026</span>
                    </div>
                    <div class="history-item">
                        <span class="icon">🕒</span> <span class="text">Fortaleza → Rio de Janeiro</span> <span class="date">22/06/2026</span>
                    </div>
                    <div class="history-item">
                        <span class="icon">🕒</span> <span class="text">Hotéis em Gramado</span> <span class="date">21/06/2026</span>
                    </div>
                    <div class="history-item">
                        <span class="icon">🕒</span> <span class="text">Fortaleza → Lisboa</span> <span class="date">20/06/2026</span>
                    </div>
                    <div class="history-item">
                        <span class="icon">🕒</span> <span class="text">Hotéis em Salvador</span> <span class="date">19/06/2026</span>
                    </div>
                    <button class="btn-outline full-width mt-10">Buscar novamente</button>
                </div>
            </div>

            <!-- Saved Destinations -->
            <div class="dashboard-panel">
                <div class="panel-header">
                    <h3>Destinos salvos</h3>
                    <a href="#/destinations" class="link-btn">Ver todos</a>
                </div>
                <div class="panel-content list-content">
                    <div class="dest-item">
                        <img src="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=100&q=80" alt="Jericoacoara">
                        <span class="text">Jericoacoara</span>
                        <span class="icon text-danger">❤️</span>
                    </div>
                    <div class="dest-item">
                        <img src="https://images.unsplash.com/photo-1632709230588-46dae858dbab?auto=format&fit=crop&w=100&q=80" alt="Gramado">
                        <span class="text">Gramado</span>
                        <span class="icon text-danger">❤️</span>
                    </div>
                    <div class="dest-item">
                        <img src="https://images.unsplash.com/photo-1585208798174-6cedd86e019a?auto=format&fit=crop&w=100&q=80" alt="Lisboa">
                        <span class="text">Lisboa</span>
                        <span class="icon text-danger">❤️</span>
                    </div>
                    <div class="dest-item">
                        <img src="https://images.unsplash.com/photo-1589909202802-8f4aadce1849?auto=format&fit=crop&w=100&q=80" alt="Buenos Aires">
                        <span class="text">Buenos Aires</span>
                        <span class="icon text-danger">❤️</span>
                    </div>
                    <button class="btn-outline full-width mt-10">Explorar destinos</button>
                </div>
            </div>
        </div>

        <!-- Recommended section -->
        <div class="recommended-section">
            <div class="panel-header mb-15">
                <h3>Recomendado para você</h3>
                <a href="#" class="link-btn">Ver mais recomendações</a>
            </div>
            <div class="cards-carousel">
                <!-- Card 1 -->
                <div class="rec-card">
                    <img src="https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?auto=format&fit=crop&w=300&q=80" alt="Porto de Galinhas">
                    <div class="rec-info">
                        <h4>Porto de Galinhas</h4>
                        <span class="loc">Pernambuco</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 540</strong>
                        </div>
                    </div>
                </div>
                <!-- Card 2 -->
                <div class="rec-card">
                    <img src="https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?auto=format&fit=crop&w=300&q=80" alt="Maceió">
                    <div class="rec-info">
                        <h4>Maceió</h4>
                        <span class="loc">Alagoas</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 480</strong>
                        </div>
                    </div>
                </div>
                <!-- Card 3 -->
                <div class="rec-card">
                    <img src="https://images.unsplash.com/photo-1543007630-9710e4a00a20?auto=format&fit=crop&w=300&q=80" alt="São Paulo">
                    <div class="rec-info">
                        <h4>São Paulo</h4>
                        <span class="loc">São Paulo</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 430</strong>
                        </div>
                    </div>
                </div>
                <!-- Card 4 -->
                <div class="rec-card">
                    <img src="https://images.unsplash.com/photo-1585208798174-6cedd86e019a?auto=format&fit=crop&w=300&q=80" alt="Lisboa">
                    <div class="rec-info">
                        <h4>Lisboa</h4>
                        <span class="loc">Portugal</span>
                        <div class="rec-price">
                            <span class="from">A partir de</span>
                            <strong>R$ 2.800</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    return container;
}
