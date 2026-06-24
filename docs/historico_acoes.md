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

---

## 🎯 Onde Paramos / Próximos Passos
- A infraestrutura de autenticação via Google e Facebook está totalmente funcional, autorizada e parametrizada em produção.
- As próximas atividades devem focar em finalizar a implementação do mapa iterativo no frontend e backend (baseado no `accommodation_service` e no arquivo `map.py` que estava sendo editado).
