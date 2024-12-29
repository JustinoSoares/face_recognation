# Usa uma imagem Python como base
FROM python:3.9-slim

# Atualiza os pacotes do sistema e instala dependências do face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    v4l-utils \
    && apt-get clean

# Instala o dlib e outras dependências
RUN pip install --no-cache-dir dlib

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY app/ /app/

# Instala as dependências do Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponha a porta 5000 para o Flask
EXPOSE 5000

# Comando para iniciar o aplicativo
CMD ["python", "/app/main.py"]
