export function renderDestinations() {
    const container = document.createElement('div');
    container.className = 'page-container';

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 class="page-title">Destinos Salvos</h1>
            <button class="btn-magic" onclick="window.openAIDrawer()">✨ Criar Roteiro Mágico</button>
        </div>
        
        <div class="cards-carousel">
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
        </div>

        <!-- AI Magic Drawer -->
        <div class="ai-drawer-overlay" id="ai-overlay"></div>
        <div class="ai-drawer" id="ai-drawer">
            <div class="ai-header">
                <h2>✨ Roteiro Inteligente</h2>
                <button class="ai-close" onclick="window.closeAIDrawer()">×</button>
            </div>
            <div class="ai-body" id="ai-chat-body">
                <div class="ai-chat-msg">
                    <div class="ai-avatar">IA</div>
                    <div class="ai-bubble">Olá! Eu sou sua assistente de viagens. Escolha um destino e quantos dias você pretende ficar para eu montar um roteiro inesquecível para você!</div>
                </div>
                
                <div class="ai-input-group mt-10">
                    <label>Para onde você quer ir?</label>
                    <input type="text" id="ai-dest" value="Jericoacoara" placeholder="Ex: Gramado, Paris...">
                </div>
                <div class="ai-input-group">
                    <label>Quantos dias?</label>
                    <input type="number" id="ai-days" value="5" min="1">
                </div>
                
                <button class="btn-magic" id="btn-generate-ai">Gerar Roteiro</button>
            </div>
        </div>
    `;

    // Global UI functions
    window.openAIDrawer = () => {
        document.getElementById('ai-overlay').classList.add('show');
        document.getElementById('ai-drawer').classList.add('open');
    };
    
    window.closeAIDrawer = () => {
        document.getElementById('ai-overlay').classList.remove('show');
        document.getElementById('ai-drawer').classList.remove('open');
    };

    // AI Generation Mock Logic
    setTimeout(() => {
        const btnGen = container.querySelector('#btn-generate-ai');
        if(!btnGen) return;

        btnGen.addEventListener('click', () => {
            const dest = document.getElementById('ai-dest').value;
            const days = document.getElementById('ai-days').value;
            const chatBody = document.getElementById('ai-chat-body');
            
            // Remove form
            btnGen.style.display = 'none';
            document.getElementById('ai-dest').parentElement.style.display = 'none';
            document.getElementById('ai-days').parentElement.style.display = 'none';

            // Add loading
            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'ai-chat-msg';
            loadingMsg.innerHTML = \`<div class="ai-avatar">IA</div><div class="ai-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>\`;
            chatBody.appendChild(loadingMsg);
            
            // Simulate 2.5s network delay
            setTimeout(() => {
                chatBody.removeChild(loadingMsg);
                
                const responseMsg = document.createElement('div');
                responseMsg.className = 'ai-chat-msg';
                responseMsg.innerHTML = \`<div class="ai-avatar">IA</div><div class="ai-bubble">
                    <strong>Roteiro Mágico: \${dest} em \${days} dias</strong><br><br>
                    <strong>Dia 1:</strong> Chegada e reconhecimento do local. Sugiro um jantar leve perto da praia.<br><br>
                    <strong>Dia 2:</strong> Passeio completo pelos principais pontos turísticos. Não esqueça a câmera!<br><br>
                    <strong>Dia \${days}:</strong> Compras locais e preparação para o retorno.
                </div>\`;
                chatBody.appendChild(responseMsg);
            }, 2500);
        });
    }, 100);

    return container;
}
