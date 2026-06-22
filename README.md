# ✈️ Partiu Viajar - Metabuscador de Passagens Aéreas Premium

O **Partiu Viajar** é um metabuscador de passagens aéreas de alto desempenho projetado com uma arquitetura moderna e reativa. A aplicação realiza buscas em tempo real em diversos agregadores de voos (Google Flights, Kayak, etc.), consolida as informações e as disponibiliza aos usuários através de uma interface moderna e com recursos interativos premium.

---

## 🚀 Funcionalidades Premium

### 1. Busca Reativa Assíncrona e Streaming em Tempo Real
* **Dramatiq Workers & Redis**: As buscas pesadas de raspagem (scrapers que controlam navegadores via Playwright) são enviadas em segundo plano para filas do Redis gerenciadas por workers do Dramatiq.
* **Server-Sent Events (SSE)**: Conforme os resultados de cada coletor vão ficando prontos e salvos em cache, eles são disparados em tempo real de volta para a tela do usuário através de conexões de streaming aberto (`EventSource`).

### 2. Autocomplete Inteligente (Typeahead Search)
* Dropdown personalizado com visual glassmorphic para os campos de **Origem** e **Destino**.
* Suporta buscas inteligentes por código de aeroporto (IATA), nome da cidade ou estado, com filtro de acentuação e suporte a navegação por teclado (Setas e Enter).

### 3. Filtros Interativos e Ordenação Dinâmica (Client-side)
* Filtro instantâneo por quantidade de paradas (Sem escalas, 1 parada, 2+ paradas).
* Filtro de preço máximo com seletor deslizante (*slider*).
* Filtros por companhias aéreas dinâmicos (gerados a partir das empresas que aparecem na busca).
* Ordenação rápida por: **Mais Barato**, **Mais Rápido** e **Melhor Relação Custo-Benefício**.

### 4. Gráficos de Histórico de Preços
* Modal com gráfico de linha interativo em cada card de voo (utilizando Chart.js) mostrando a evolução e o histórico de preços daquele voo específico para ajudar o usuário a decidir o melhor momento de compra.

### 5. Alertas de Preços
* Os usuários podem cadastrar seus e-mails e/ou chat IDs do Telegram para monitorar rotas específicas.
* Um agendador periódico (`APScheduler`) verifica a cada 10 minutos no banco se há ofertas abaixo do valor alvo estipulado pelo usuário.

### 6. Combo Inteligente (Ida e Volta)
* Quando o usuário realiza buscas de ida e volta, o sistema calcula e destaca automaticamente o melhor e mais barato "Combo" de passagem de ida e volta combinadas.

---

## 🛠️ Stack Tecnológica

* **Backend**:
  * [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn (API assíncrona)
  * [Dramatiq](https://dramatiq.io/) (Fila de tarefas assíncronas)
  * [Playwright Python](https://playwright.dev/python/) (Automação de navegador para raspagem)
  * [SQLAlchemy](https://www.sqlalchemy.org/) + [Asyncpg](https://github.com/MagicStack/asyncpg) (Persistência assíncrona)
  * [APScheduler](https://apscheduler.readthedocs.io/) (Agendador de tarefas periódicas)
* **Bancos e Cache**:
  * [PostgreSQL](https://www.postgresql.org/) (Banco de dados relacional persistente)
  * [Redis](https://redis.io/) (Broker de mensageria, pub/sub e cache temporário)
* **Frontend**:
  * HTML5 Semântico e Vanilla CSS3 (Design responsivo premium com temas escuros e glassmorphism)
  * Vanilla Javascript moderno (manipulação de DOM, conexões SSE e eventos)
  * [Chart.js](https://www.chartjs.org/) (Renderização dos gráficos de preço)

---

## 📁 Estrutura de Diretórios do Projeto

```text
Buscador/
├── docs/
│   └── deployment.md          # Guia passo a passo de deploy em nuvem (Linux)
├── flight_engine/
│   ├── api/                   # Rotas REST e controladores da API
│   ├── application/           # Lógica de aplicação e comandos
│   ├── core/                  # Configurações globais e segurança
│   ├── domain/                # Entidades e regras de domínio puro
│   ├── infrastructure/        # Banco de dados, adaptadores e coletores/scrapers
│   ├── jobs/                  # Agendadores recorrentes (alertas)
│   ├── scripts/               # Scripts de inicialização e migrações
│   ├── static/                # Arquivos estáticos front-end (index.html, app.js, style.css)
│   ├── workers/               # Declaração de tarefas (Dramatiq actors)
│   ├── pyproject.toml         # Definições de projeto Python e dependências
│   └── requirements.txt       # Arquivo de dependências para o pip
└── scratch/                   # Scripts rápidos de teste e manutenção
```

---

## 💻 Como Rodar o Projeto Localmente

### Pré-requisitos
* Python 3.11 ou superior instalado.
* Banco de dados PostgreSQL configurado.
* Servidor Redis ativo.

### Passo 1: Configurar Variáveis de Ambiente
Crie um arquivo `.env` dentro da pasta `flight_engine` seguindo este modelo:
```ini
DATABASE_URL="postgresql+asyncpg://usuario:senha@ip_do_postgres:5432/flights_db"
REDIS_URL="redis://ip_do_redis:6379/0"
```

### Passo 2: Configurar o Ambiente Virtual Python
```bash
cd flight_engine
python -m venv venv

# No Windows (PowerShell):
venv\Scripts\Activate.ps1
# No Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### Passo 3: Criar as Tabelas do Banco de Dados
```bash
python scripts/migrate.py
```

### Passo 4: Iniciar o Servidor da API
```bash
python scripts/start_api.py
```
A API e o painel web estarão disponíveis em: **http://localhost:8000**

### Passo 5: Iniciar o Worker em Segundo Plano
Abra outro terminal, ative o ambiente virtual e execute:
```bash
python scripts/start_worker.py
```

---

## 🚀 Implantação em Nuvem

Para informações detalhadas sobre como subir esta aplicação para produção em servidores Linux de nuvem (AWS, DigitalOcean, Azure, etc.) configurando Nginx, Systemd de persistência e SSL automático, consulte o nosso **[Guia de Implantação em Produção](file:///c:/Users/alexa/Buscador/docs/deployment.md)**.

---

## 🧪 CI/CD

O projeto possui integração contínua (CI) configurada via GitHub Actions. Os testes automatizados rodarão sempre que um Pull Request receber as labels `test` ou `manual`.

