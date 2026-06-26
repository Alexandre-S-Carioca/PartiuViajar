# 📜 Histórico de Ações e Solução de Problemas

Este documento mantém o registro das últimas manutenções, correções de bugs e configurações realizadas no ambiente de produção e desenvolvimento do **Partiu Viajar**. Serve como um guia para sabermos onde paramos e como os problemas recentes foram resolvidos.

---

## 📅 24 de Junho de 2026 (Manhã)

**Contexto:** O projeto estava recém-migrado para suportar OAuth2 (Google/Facebook) e sendo testado em um ambiente de produção na Nuvem (Ubuntu VPS na Oracle Cloud) através do Docker Compose.

### 1. Correção de Redirecionamento OAuth (Celular vs Localhost)
- **Problema:** Ao testar o login do Facebook/Google pelo celular, a página exibia `ERR_CONNECTION_REFUSED` tentando acessar `localhost:8000`.
- **Causa:** O contêiner da API em produção não estava recebendo a variável de ambiente `SITE_URL`, fazendo o sistema usar o valor padrão de segurança (`http://localhost:8000`).
- **Ação:** Adicionado `- SITE_URL=${SITE_URL}` ao bloco de environment do serviço `api` no `docker-compose.prod.yml`.

### 2. Tratamento de Erro de Timeout no Callback do Google (Erro 504)
- **Problema:** A rota `/api/v1/auth/google/callback` demorava muito para responder, resultando em um `504 Gateway Time-out` no Nginx.
- **Ação:** Refatorado o arquivo `flight_engine/api/routes/auth.py`. Foi incluído um tempo limite de 15 segundos (`httpx.AsyncClient(timeout=15.0)`) e blocos `try-except` para capturar falhas de rede (`httpx.RequestError`). Isso evita que o Nginx derrube a requisição silenciosamente, garantindo que a API retorne um erro `500` claro e com logs adequados.

### 3. Resolução de Conflitos de Porta no Docker
- **Problema:** O banco de dados falhava ao subir acusando `failed to bind host port 0.0.0.0:5432/tcp: address already in use`.
- **Causa:** O comando `docker-compose up` foi rodado sem especificar o arquivo `-f docker-compose.prod.yml`, o que carregou o ambiente de desenvolvimento, tentando expor a porta 5432 para fora (entrando em conflito com sessões antigas ou serviços nativos).
- **Ação:** Instruído o uso correto das flags de limpeza e produção (`docker-compose down --remove-orphans` e `docker-compose -f docker-compose.prod.yml up -d --build`).

### 4. Correção Crítica de Conexão com Banco de Dados e Senhas com Caracteres Especiais (Erro 502)
- **Problema:** O servidor Nginx retornava `502 Bad Gateway` logo após o deploy porque a API (`Uvicorn`) sofria um "Crash" (TimeoutError) antes de ficar pronta.
- **Causa:** 
  1. O arquivo `docker-compose.prod.yml` estava passando a variável `DATABASE_URL` inteira montada.
  2. O SQLAlchemy quebra a URL se a senha (vinda do `.env`) contiver caracteres especiais como `@` ou `#`, achando que aquilo faz parte do endereço do Host.
  3. O banco de dados correto da produção não era o contêiner interno do Docker, mas sim um banco externo no IP `163.176.228.2`.
- **Ação:** O `docker-compose.prod.yml` foi reescrito. Removemos a injeção estática de `DATABASE_URL` e passamos as peças soltas (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`) e configuramos o `DB_HOST=${DB_HOST:-163.176.228.2}`. Dessa forma, o próprio código Python (`core/config.py`) assume a responsabilidade de montar a URL e realiza o `URL Encode` automático da senha. O problema foi resolvido sem que o usuário precisasse alterar a senha de produção.

### 5. Resolução do Erro de Domínio no Facebook Login
- **Problema:** Ao tentar realizar o login com o Facebook, a página exibia a mensagem: "O domínio dessa URL não está incluído nos domínios do app".
- **Causa:** No painel de desenvolvedores do Facebook, a URL de callback (`https://www.partviajar.com.br/api/v1/auth/facebook/callback`) estava sendo inserida na seção incorreta (Compartilhamentos) em vez das configurações exclusivas do produto "Login do Facebook". Além disso, estava faltando a URL da Política de Privacidade para habilitar o salvamento.
- **Ação:** Instruções detalhadas para navegar no novo layout do *Facebook Developers* (Casos de uso -> Autenticação e criação da conta -> Configurações -> URIs de redirecionamento do OAuth válidos), onde a URL com `https://` foi corretamente inserida e salva, liberando o login.

### 7. Refatoração Responsiva dos Cartões de Resultado
- **Problema:** Em dispositivos móveis, a listagem de voos e hotéis estava esmagando o texto na horizontal, devido a um `display: flex` engessado.
- **Ação:** As regras inline foram substituídas pelas classes CSS `.result-card`, `.info-section` e `.price-section`. Foi criada uma regra de `@media (max-width: 600px)` no `index.css` que converte a visualização para colunas e expande a foto do hotel como um banner, garantindo fluidez no celular. O parâmetro de versão do CSS e JS no `index.html` foi atualizado (Cache Busting) para forçar o recarregamento.

### 8. Busca Inteligente no Painel de Usuário
- **Problema:** A barra de buscas dentro do painel (`dashboard.html`) exibia sempre "CHECK-IN", "CHECK-OUT" e "HÓSPEDES", independentemente da aba selecionada. Além disso, não possuía filtro de "Só Ida".
- **Ação:** Inserimos seletores dinâmicos (Radio Buttons) para "Ida e Volta / Só Ida" na interface. No arquivo `app.js`, injetamos ouvintes de evento para que, ao clicar na aba "Passagens", os rótulos mudem para "IDA/VOLTA/PASSAGEIROS" e para que o campo de volta seja escondido quando a opção "Só Ida" é ativada.

### 9. Calibragem de Contraste no Tema Claro
- **Problema:** O modo claro do painel não oferecia separação visual suficiente entre os cartões brancos e o fundo cinza clarinho (`#F3F4F6`), apagando as sombras.
- **Ação:** Alteramos as variáveis do modo claro (`[data-theme="light"]`). O fundo principal foi escurecido para `#E5E7EB`, a cor das bordas dos cartões de dashboard mudou para `#D1D5DB` e as opacidades de `--shadow-sm`, `--shadow-md` e `--shadow-lg` foram triplicadas.

### 10. Limpeza de Dados Fictícios e Interação de Recomendações
- **Problema:** O painel (Dashboard) estava pré-preenchido com números falsos e listas fictícias (buscas, alertas, destinos), o que causava estranheza em novos usuários cadastrados. Além disso, as recomendações no rodapé eram estáticas e não levavam a lugar algum.
- **Ação:** No arquivo `dashboard.js`, zeramos os números estatísticos do placar principal (Pesquisas, Favoritos, Alertas, Destinos). Para as colunas de "Últimas buscas", "Alertas" e "Destinos salvos", implementamos mensagens e ícones amigáveis de estado vazio (*empty states*). Também transformamos as quatro fotos de recomendação no rodapé em links embutidos (`<a>`) que redirecionam os usuários para o Google Travel (com o termo de busca pré-preenchido para aquele destino), proporcionando interatividade imediata.

### 11. Sincronização de Histórico da Landing Page com o Dashboard
- **Problema:** Apenas a barra de buscas interna do Dashboard estava salvando o histórico no cache do navegador. Se o usuário fizesse uma pesquisa a partir da tela principal (Landing Page com o mapa), a busca não ficava registrada, e o painel continuava exibindo que o histórico estava vazio.
- **Ação:** Injetamos a mesma rotina de salvamento (`localStorage`) no evento de envio do formulário de buscas dentro de `flight_engine/static/app.js`. Além disso, incrementamos a versão do script no arquivo HTML (`v=7`) para forçar os navegadores a limparem o cache. Com isso, toda busca feita em qualquer parte do site agora alimenta o painel de bordo perfeitamente.

### 12. Mapa Interativo com Leaflet e OpenStreetMap
- **Ação:** O frontend foi modificado (`app.js` e `index.html`) para acomodar um mapa interativo ao lado dos resultados de hotéis e pacotes unificados. O layout foi adaptado para "Grid" de forma que o mapa fique com posição fixa (sticky) ao longo da rolagem da lista de resultados. Foi utilizada a biblioteca de código aberto `Leaflet.js`.

### 13. Geolocalização Real de Hotéis via Nominatim
- **Problema:** O scraper do Booking gerava hotéis sem latitude/longitude ou espalhados em coordenadas globais imprecisas.
- **Ação:** No backend (`accommodation_service.py`), sempre que o scraper de hotéis atua, é feita uma chamada em tempo real à API pública do **Nominatim (OpenStreetMap)** para encontrar a latitude e longitude exatas da cidade pesquisada. Os hotéis recebem uma sutil variação aleatória de até 2km dessa coordenada principal, fazendo com que os "pins" no mapa surjam realistas ao longo do mapa urbano/litoral.

### 14. Refinamentos da UI: Links de Afiliados, Logo e Menus
- **Ação:** Dentro dos "pins" (balões popup) do Leaflet no mapa, foi injetado um botão com o link oficial de afiliado do Booking, passando os parâmetros dinâmicos de destino, check-in, check-out e adultos. O menu lateral sofreu otimizações: a aba "Destinos salvos" foi removida a pedido do usuário; e a logomarca no canto esquerdo da sidebar tornou-se clicável, operando um *reset* dos campos de busca e o fechar do modal, enviando o usuário de volta para o Dashboard.

### 15. Dashboard: Geolocalização, POIs (Overpass API) e Busca Dinâmica no Mapa
- **Ação:** O painel principal (Dashboard) recebeu um upgrade maciço no seu mapa interativo:
  - **Localização em Tempo Real:** Adição de um botão no topo direito (📍) que aciona a API de geolocalização do navegador do usuário, com requisição de Alta Precisão (`enableHighAccuracy`). O mapa automaticamente foca onde o usuário está e injeta um marcador local.
  - **Radar de POIs (Pontos de Interesse):** Sem necessidade de sobrecarregar o backend com requisições, o próprio frontend (JavaScript) escuta o evento `moveend` do Leaflet e dispara uma busca para a **Overpass API** do OpenStreetMap, descobrindo 🏨 Hotéis, ✈️ Aeroportos e 🚌 Rodoviárias visíveis no enquadramento, preenchendo a região com ícones dinâmicos personalizados.
  - **Afiliados nos POIs:** Ao clicar em um hotel no mapa, o pop-up dinâmico agora gera um botão "Reservar no Booking" com a ID de afiliado do usuário, pré-preenchendo o nome do hotel exato na busca do Booking. Aeroportos redirecionam com um botão azul para o Skyscanner.
  - **Barra de Busca Inteligente no Mapa:** Para explorar lugares globais, foi inserida uma barra de texto acima do mapa. O usuário escreve uma cidade (Ex: Tóquio), a requisição bate na API do Nominatim, encontra as coordenadas e centraliza a tela ali em segundos.
  - **Modo de Expansão (Modal Suspenso):** Adição de um botão "⛶" para ampliar o mapa. Ao invés de usar o recurso bruto de tela cheia do navegador, o mapa se torna um modal suspenso, ocupando 85% da tela com um sombreamento de fundo (estilo cinema). Também foi adicionado um botão flutuante inteligente "✖" para sair do modo de expansão de forma intuitiva, sem sobrescrever ou vazar eventos de clique para o Leaflet.

## 16. Resolução Crítica de Bugs de Deploy (Produção)
- **Data:** 25/06/2026
- **Problema 1 (Erro 500 / Tela Branca):** Após o deploy na Oracle Cloud, o site retornou "Internal Server Error". A causa raiz foi identificada no `Dockerfile`: a pasta `static` estava sendo copiada para o diretório incorreto (`/app/flight_engine/static`), enquanto o código do FastAPI (`api/main.py`) resolvia o caminho absoluto para `/app/static`. Isso fazia o FastAPI tentar ler o `index.html` em uma pasta recém-criada vazia, gerando um `FileNotFoundError` que derrubava a requisição.
- **Ação 1:** O `Dockerfile` foi corrigido para mapear exatamente a pasta usando `COPY static /app/static`, equalizando os caminhos.
- **Problema 2 (Arquivos Estáticos não atualizando):** Mesmo com o build, as alterações de CSS/JS (como o mapa suspenso) não refletiam no navegador, devido ao cache de imagem do Docker e falta de mapeamento direto.
- **Ação 2:** Adicionada a instrução de volume `- ./static:/app/static` no serviço `api` dentro do `docker-compose.prod.yml`. Isso faz com que qualquer alteração nos arquivos estáticos seja espelhada imediatamente para o contêiner em execução, sem necessidade de rebuild, seguindo a Regra de Ouro definida no projeto.

---

## 📍 Onde Paramos / Próximos Passos
- O "Buscador de Viagens" já superou o escopo de ser um simples agregador e evoluiu para uma central de planejamento visual extremamente útil (Dashboard).
- As rotinas front-end estão altamente integradas e independentes do backend para certas visualizações geoespaciais (Leaflet, Overpass API, Nominatim).
- Os próximos passos ideais podem envolver aprimorar o módulo de Rastreio de Voos e garantir que a página de Checkout e Reservas (se for haver uma local) siga os links de afiliado com consistência total.
