# Utiliza a imagem oficial do Python na versão mais atual
FROM python:latest

# Instala o netcat (usado para checar a disponibilidade do banco)
RUN apt-get update && apt-get install -y netcat-openbsd

# Cria um ambiente virtual
RUN python -m venv /venv

# Adiciona o diretório bin do venv ao PATH
ENV PATH="/venv/bin:$PATH"

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências e os instala
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo o projeto para dentro do container
COPY . /app

# Garante que o entrypoint tenha permissão de execução
RUN chmod +x /app/entrypoint.sh

# Expõe a porta 8080 para acesso externo
EXPOSE 8080

# Define o entrypoint, que automatiza as tarefas ao subir o container
ENTRYPOINT ["/app/entrypoint.sh"]
