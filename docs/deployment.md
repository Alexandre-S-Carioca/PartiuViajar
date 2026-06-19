# Guia de Implantação em Produção - Partiu Viajar

Este documento fornece as instruções passo a passo para implantar a aplicação **Partiu Viajar** em uma instância de produção na nuvem (preferencialmente utilizando Linux/Ubuntu Server).

---

## 🏗️ Visão Geral da Arquitetura

A aplicação é composta por:
1. **API Web (FastAPI/Uvicorn)**: Servidor web assíncrono que atende a interface do usuário e disponibiliza os endpoints HTTP e SSE (Server-Sent Events) para streaming de buscas.
2. **Worker de Background (Dramatiq)**: Processador de fila que executa a raspagem assíncrona de passagens aéreas (através de subprocessos com Playwright).
3. **Mensageria e Cache (Redis)**: Gerencia a fila de tarefas do Dramatiq e canais Pub/Sub para streaming dinâmico de voos.
4. **Banco de Dados (PostgreSQL)**: Persiste histórico de voos coletados e assinaturas de alertas de preços.

---

## 🛠️ 1. Instalação de Dependências de Sistema

Conecte-se à sua instância do servidor via SSH e instale os pacotes básicos necessários do Linux:

```bash
sudo apt update
sudo apt upgrade -y

# Instalação do Python, Pip, Venv, Git e compiladores básicos
sudo apt install python3-pip python3-venv python3-dev git build-essential -y

# Instalação do PostgreSQL e Redis Server (se for hospedá-los na mesma máquina)
sudo apt install postgresql postgresql-contrib redis-server -y
```

---

## 📁 2. Clonagem e Configuração do Ambiente

1. Clone o repositório da aplicação na pasta de deploy (ex: `/var/www/partiu-viajar`):
   ```bash
   sudo mkdir -p /var/www/partiu-viajar
   sudo chown -R $USER:$USER /var/www/partiu-viajar
   cd /var/www/partiu-viajar
   git clone <URL_DO_SEU_REPOSITORIO> .
   ```

2. Crie e ative o ambiente virtual do Python dentro da pasta `flight_engine`:
   ```bash
   cd flight_engine
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências declaradas:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🚨 3. Configuração do Playwright (Essencial para o Scraper)

Como o projeto realiza raspagem em segundo plano, o Playwright precisa baixar o navegador Chromium e as bibliotecas gráficas nativas do Linux (mesmo rodando em modo Headless):

```bash
# 1. Instala o binário do Chromium
playwright install chromium

# 2. Instala as dependências de sistema do Linux necessárias para execução headless
sudo playwright install-deps
```

---

## 🔑 4. Configuração das Variáveis de Ambiente

Crie o arquivo `.env` dentro da pasta `flight_engine`:

```bash
nano .env
```

Preencha com a seguinte estrutura de produção:

```ini
# Configuração da Aplicação
APP_NAME="Partiu Viajar"
DEBUG=False

# Banco de Dados PostgreSQL (Altere usuário, senha, ip e db_name)
DATABASE_URL="postgresql+asyncpg://seu_usuario:sua_senha@127.0.0.1:5432/flights_db"

# Redis Server
REDIS_URL="redis://127.0.0.1:6379/0"
```

---

## 🗄️ 5. Inicialização do Banco de Dados

Caso ainda não tenha criado o banco de dados e as tabelas, execute os comandos do PostgreSQL:

```bash
# Acessar o Postgres
sudo -i -u postgres psql

# Criar banco de dados
CREATE DATABASE flights_db;

# Criar usuário e conceder acessos
CREATE USER seu_usuario WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE flights_db TO seu_usuario;
\q
```

Após o banco de dados estar configurado, execute o script de migração para gerar as tabelas do projeto (`flights` e `price_alerts`):
```bash
python scripts/migrate.py
```

---

## ⚙️ 6. Gerenciamento de Processos (Systemd)

Para manter os serviços rodando continuamente e reiniciar automaticamente em caso de falhas ou reinicialização do servidor, usaremos o gerenciador nativo do Linux, o **Systemd**.

### A. Serviço da API Web (FastAPI)
Crie o arquivo: `sudo nano /etc/systemd/system/viajar-api.service`
```ini
[Unit]
Description=Partiu Viajar - FastAPI API Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/partiu-viajar/flight_engine
ExecStart=/var/www/partiu-viajar/flight_engine/venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
EnvironmentFile=/var/www/partiu-viajar/flight_engine/.env

[Install]
WantedBy=multi-user.target
```

### B. Serviço do Background Worker (Dramatiq)
Crie o arquivo: `sudo nano /etc/systemd/system/viajar-worker.service`
```ini
[Unit]
Description=Partiu Viajar - Dramatiq Background Worker
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/partiu-viajar/flight_engine
ExecStart=/var/www/partiu-viajar/flight_engine/venv/bin/python -m dramatiq workers.tasks -p 2 -t 2
Restart=always
EnvironmentFile=/var/www/partiu-viajar/flight_engine/.env

[Install]
WantedBy=multi-user.target
```

### Habilitar e Iniciar os Serviços
Execute no terminal:
```bash
sudo systemctl daemon-reload
sudo systemctl enable viajar-api viajar-worker
sudo systemctl start viajar-api viajar-worker
```

Você pode checar o status e ler os logs em tempo real usando:
```bash
sudo systemctl status viajar-api
sudo journalctl -u viajar-worker -f
```

---

## 🛡️ 7. Configuração do Reverse Proxy com Nginx

O Nginx receberá as requisições web externas na porta `80`/`443` e as direcionará para a porta interna do Uvicorn (`8000`), gerenciando também a compressão e segurança.

1. Instale o Nginx:
   ```bash
   sudo apt install nginx -y
   ```

2. Crie a configuração de host virtual em `sudo nano /etc/nginx/sites-available/partiu-viajar`:
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com.br; # Altere para o seu domínio ou IP público da nuvem

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # IMPORTANTE: Desativar buffering para que o streaming de voos (Server-Sent Events) funcione corretamente!
           proxy_buffering off;
           proxy_cache off;
       }
   }
   ```

3. Ative o host e reinicie o Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/partiu-viajar /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

---

## 🔒 8. SSL (HTTPS) com Let's Encrypt (Certbot)

Para garantir segurança ponta-a-ponta e habilitar HTTPS gratuitamente:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com.br
```

Siga as instruções na tela. O Certbot irá alterar automaticamente seu arquivo Nginx para redirecionar HTTP para HTTPS e instalar os certificados renováveis.

---

## 🛠️ 9. Solução de Problemas Comuns (Troubleshooting)

### Erro: `OSError: [Errno 9] Bad file descriptor` com Playwright
* **Causa**: Tentativa de instanciar o browser em threads filhas no Windows.
* **Solução**: Já configurada por padrão no código. O worker do Dramatiq executa o scraper em subprocessos independentes (`scripts/run_scraper.py`), eliminando este problema no ambiente de desenvolvimento Windows e garantindo compatibilidade total no Linux de produção.

### As buscas demoram e dão Timeout (504 Gateway Timeout no Nginx)
* **Causa**: Os scrapers de terceiros podem demorar mais do que o timeout padrão do proxy do Nginx.
* **Solução**: Certifique-se de que a linha `proxy_buffering off;` está ativa nas configurações do Nginx. Isso garante que cada voo encontrado seja enviado ao navegador do usuário imediatamente, sem esperar toda a raspagem acabar.

### Problemas com Conexão de Rede no Redis ou PostgreSQL
* **Causa**: Serviços não configurados para ouvir o endereço correto ou firewalls locais bloqueando portas.
* **Solução**:
  * Para o Redis local: certifique-se de que o arquivo `/etc/redis/redis.conf` possui a diretiva `bind 127.0.0.1` ou `bind 0.0.0.0` ativa e que o serviço foi reiniciado.
  * Para o Postgres local: verifique `/etc/postgresql/.../main/postgresql.conf` (`listen_addresses = '*'`) e `pg_hba.conf` para liberar a conexão.
