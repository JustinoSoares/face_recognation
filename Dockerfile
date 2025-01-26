# Usando a imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie os arquivos do seu projeto para dentro do contêiner
COPY . .

# Atualize o pip
RUN pip install --upgrade pip

# Instalar dependências do sistema necessárias para dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências do Python
RUN pip install -r requirements.txt

# Exponha a porta que sua aplicação vai usar (por exemplo, 5000)
EXPOSE 5000

# Comando para rodar a aplicação (ajuste conforme necessário)
CMD ["python", "src/main.py"]
