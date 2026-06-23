# Configuração de Domínio e Acesso

Este documento descreve os passos para configurar o domínio `www.partviajar.com.br` no Registro.br e apontá-lo para a infraestrutura na Oracle Cloud.

## 1. Configurar Apontamentos DNS (Registro.br)

Para vincular o domínio ao endereço IP do servidor:

1. Acesse sua conta no [Registro.br](https://registro.br).
2. Selecione o domínio `partviajar.com.br`.
3. Na seção **DNS**, clique em **Editar Zona** ou **Configurar Zona DNS**.
4. Adicione as seguintes entradas:

   **Registro Principal (sem www):**
   - **Tipo:** `A`
   - **Nome:** *(deixar em branco)*
   - **Dados:** `[INSERIR_IP_PUBLICO_DA_ORACLE_AQUI]`

   **Registro Secundário (com www):**
   - **Tipo:** `A`
   - **Nome:** `www`
   - **Dados:** `[INSERIR_IP_PUBLICO_DA_ORACLE_AQUI]`

5. Salve as alterações.
> **Nota:** A propagação DNS pode levar de alguns minutos até algumas horas para refletir globalmente.

## 2. Liberar Acesso no Servidor (Oracle Cloud)

Para que as requisições web cheguem à aplicação, é necessário abrir as portas 80 (HTTP) e 443 (HTTPS) na nuvem e no firewall interno da máquina.

### 2.1 Security Lists (Painel da Oracle Cloud)
1. Acesse o painel da Oracle Cloud.
2. Vá em **Compute** > **Instances** e selecione sua instância.
3. Clique na **Subnet** associada à instância (na seção *Primary VNIC*).
4. Em **Security Lists**, edite a lista padrão e adicione as seguintes **Ingress Rules**:
   - **Regra HTTP:** Source `0.0.0.0/0`, Protocol `TCP`, Destination Port `80`
   - **Regra HTTPS:** Source `0.0.0.0/0`, Protocol `TCP`, Destination Port `443`

### 2.2 Firewall Interno (iptables - Linux/Ubuntu)
Conecte-se à máquina via SSH e execute os comandos abaixo para liberar o tráfego no firewall local e salvar as regras permanentemente:
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

## 3. Configurar Proxy Reverso e HTTPS (Docker)

Como a API roda na porta `8000` (definido no `docker-compose.yml`), precisamos de um serviço na frente dela para receber as requisições web (portas 80 e 443) e criar o certificado de segurança (HTTPS).

### Passo a Passo

1. **Adicionar o Proxy no Docker Compose:**
   Será necessário adicionar um serviço de proxy reverso, como **Caddy** (recomendado por gerar o SSL automaticamente) ou **Nginx**, no arquivo `docker-compose.yml`.

2. **Geração do Certificado SSL (Let's Encrypt):**
   O proxy deverá ser configurado para interceptar o tráfego dos domínios `partviajar.com.br` e `www.partviajar.com.br`. Ele irá contatar a autoridade Let's Encrypt automaticamente para provisionar e renovar o certificado de criptografia, ativando a conexão segura (`https://`).

3. **Mapeamento de Portas:**
   Apenas o Proxy Reverso deve expor as portas `80` e `443` para a internet. O contêiner da `api` deverá ter as suas portas públicas removidas e comunicar-se com o proxy exclusivamente pela rede interna do Docker.

> **Exemplo de fluxo esperado:**
> *Visitante* ➡️ *HTTPS (Porta 443)* ➡️ *Proxy Reverso (Caddy/Nginx)* ➡️ *API FastAPI (Porta 8000 na rede Docker)*.

