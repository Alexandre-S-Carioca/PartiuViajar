FROM python:3.11-slim-bookworm

# Evitar criação de arquivos .pyc e não bufferizar stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# O Playwright baixará os navegadores para cá
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Instalar dependências de sistema necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY flight_engine/requirements.txt .

# Atualizar pip e instalar pacotes Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar navegadores do Playwright (apenas o Chromium para diminuir o tamanho)
# e suas dependências de SO nativas
RUN playwright install chromium && \
    playwright install-deps chromium

# Copiar o código fonte do backend para a imagem
COPY flight_engine /app/flight_engine
COPY static /app/static

# Definir o workdir principal como a pasta do flight_engine
WORKDIR /app/flight_engine

# A porta padrão que a API irá ouvir
EXPOSE 8000
