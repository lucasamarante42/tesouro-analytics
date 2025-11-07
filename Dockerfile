# Imagem base leve e atualizada
FROM python:3.11-slim AS base

# Diretório principal da aplicação
WORKDIR /app

# Evita cache e buffers desnecessários
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema (necessárias para pandas, celery e outros)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar um usuário não-root (boa prática de segurança) e o grupo antes de usar no chown
RUN useradd -m appuser

# Copiar e instalar as dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY app /app/app

# Criar diretório de dados e logs
RUN mkdir -p /data /app/logs && chown -R appuser:appuser /data /app/logs

USER appuser

# Variáveis de ambiente padrão
ENV DATA_DIR=/data \
    PYTHONPATH=/app

# Expor porta (caso precise rodar API local ou FastAPI futuramente)
EXPOSE 5000

# O comando padrão será definido no docker-compose (reuso da mesma imagem)
CMD ["python", "app/main.py"]
