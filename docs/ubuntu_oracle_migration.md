# 🐧 Guia Passo a Passo: Implantação no Ubuntu Server (Oracle Cloud)

Este guia foi criado especialmente para o seu cenário: conectar na máquina virtual Ubuntu 24.04 (via Windows) e configurar todo o ambiente do **Partiu Viajar**.

Como criamos a estrutura do **Docker** no passo anterior, a configuração no servidor Ubuntu será incrivelmente rápida.

---

## Passo 1: Conectar na Máquina Virtual via SSH (Windows)

Como você está no Windows, a melhor forma de acessar a VM na Oracle Cloud é usando o **PowerShell** nativo com a sua chave SSH `.key` ou `.pem`.

1. Abra o PowerShell no Windows.
2. Certifique-se de que sua chave de acesso (ex: `chave-oracle.key`) está protegida:
   - Clique com o botão direito na chave > Propriedades > Segurança > Avançado.
   - Remova heranças e deixe apenas o seu usuário do Windows com acesso de Leitura.
3. Conecte-se ao servidor (substitua o IP):
   ```powershell
   ssh -i "C:\caminho\para\sua\chave-oracle.key" ubuntu@IP_DA_MAQUINA
   ```

> [!TIP]
> Se o SSH pedir confirmação da impressão digital (`fingerprint`), digite `yes` e pressione Enter.

---

## Passo 2: Instalar Dependências no Ubuntu 24.04

Uma vez dentro do servidor Ubuntu, precisamos atualizar o sistema e instalar o **Docker** e o **Git**.

```bash
# Atualizar repositórios do Ubuntu
sudo apt update && sudo apt upgrade -y

# Instalar o Git
sudo apt install git -y

# Instalar o Docker e Docker Compose
sudo apt install docker.io docker-compose -y

# Adicionar seu usuário ao grupo do Docker para não precisar usar "sudo" sempre
sudo usermod -aG docker ubuntu
```

> [!NOTE]
> Após o comando `usermod`, você precisa sair do servidor (`exit`) e conectar novamente via SSH para as permissões do Docker aplicarem.

---

## Passo 3: Clonar o Repositório do Projeto

Agora vamos baixar o código do **Partiu Viajar** para a sua máquina Ubuntu.

```bash
# Navegue para a pasta inicial
cd ~

# Clone o seu repositório GitHub (Ajuste a URL se for privado)
git clone https://github.com/Alexandre-S-Carioca/PartiuViajar.git

# Entre na pasta
cd PartiuViajar
```

---

## Passo 4: Configurar Bancos de Dados e Acessos (PostgreSQL)

Como usamos o `docker-compose.yml`, o **PostgreSQL e o Redis** subirão automaticamente dentro dos contêineres! Você **não** precisa instalá-los separadamente no Ubuntu com `apt install postgresql`, a menos que deseje tê-los rodando de forma independente na máquina host.

> [!IMPORTANT]
> **Sobre o acesso ao PostgreSQL na Oracle Cloud:**
> Se você pretende acessar o banco de dados de fora (da sua máquina Windows), lembre-se que além do Docker expor a porta `5432`, você precisará liberar a porta `5432` nas **Listas de Segurança (Security Lists)** dentro do painel web da Oracle Cloud Infrastructure (OCI).
> E também no firewall interno do Ubuntu: `sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5432 -j ACCEPT`

### Variáveis de Ambiente
Crie o arquivo `.env` para a produção dentro do servidor:
```bash
nano .env
```
Cole o seguinte conteúdo (e altere as senhas depois se quiser):
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha_super_segura
POSTGRES_DB=flights_db
DEBUG=False
```
Salve e saia do Nano (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Passo 5: Rodar a Aplicação

Com o Docker, o processo de "Build" e "Run" é feito em um único comando. **Atenção**: Como estamos em produção, você **DEVE** utilizar o arquivo `docker-compose.prod.yml`:

```bash
# Dentro da pasta PartiuViajar
docker-compose -f docker-compose.prod.yml up --build -d
```

> [!WARNING]
> **Evitando Erro 500 e Cache de Frontend em Produção**
> Nunca utilize o comando padrão (`docker-compose up`) em produção, pois ele tentará ligar o banco de dados interno na porta `5432` conflitando com o PostgreSQL nativo do servidor Oracle e quebrando a inicialização da API (gerando Erro 502 Bad Gateway no Nginx).
> Além disso, o arquivo `docker-compose.prod.yml` já contém o volume `- ./static:/app/static`. Isso garante que qualquer arquivo CSS, JS ou HTML atualizado via `git pull` será injetado imediatamente no servidor web sem precisar refazer o build da imagem!

A flag `-d` garante que os serviços continuem rodando em segundo plano (background) mesmo que você feche o terminal do Windows.

---

## Passo 6: Expor para a Internet (Nginx Opcional)

Neste momento, a sua aplicação estará rodando na porta `8000` do servidor.
Se quiser acessá-la diretamente pelo IP sem digitar a porta, ou colocar um domínio e HTTPS:

1. Instale o Nginx:
   ```bash
   sudo apt install nginx -y
   ```
2. Crie uma configuração de proxy reverso:
   ```bash
   sudo nano /etc/nginx/sites-available/partiu-viajar
   ```
3. Adicione o seguinte conteúdo:
   ```nginx
   server {
       listen 80;
       server_name _; # Ou coloque o IP público / domínio

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           
           # Necessário para o Streaming de passagens funcionar
           proxy_buffering off;
           proxy_cache off;
       }
   }
   ```
4. Ative a configuração e reinicie:
   ```bash
   sudo ln -s /etc/nginx/sites-available/partiu-viajar /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

Pronto! Acesse o IP público da sua máquina Oracle no navegador e o metabuscador estará no ar!
