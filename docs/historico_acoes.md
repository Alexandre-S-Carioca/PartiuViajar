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

---

## 🎯 Onde Paramos / Próximos Passos
- A infraestrutura de autenticação está totalmente operante.
- O Layout responsivo do painel e os temas claro/escuro estão sólidos e limpos, apresentando dados consistentes (zerados) para novas contas.
- As próximas atividades devem focar em finalizar a implementação do mapa iterativo no frontend e backend (baseado no `accommodation_service` e no arquivo `map.py` que estava sendo editado).
