FROM python:3.9-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    cmake \
    python3-dev \
    python3-venv \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instale o prisma-client-py globalmente
RUN pip install prisma

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto para o contêiner
COPY . .

# Gere o cliente Prisma
RUN prisma generate

# Instale outras dependências do projeto
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir dlib face_recognition

# Baixe os binários necessários do Prisma com o comando fetch
RUN . venv/bin/activate \
    && prisma py fetch  # Baixa os binários necessários

# Comando de inicialização do aplicativo
CMD [".venv/bin/python", "/app/app/main.py"]

