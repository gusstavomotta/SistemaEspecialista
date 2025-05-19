FROM python:latest

# 1) Instala ferramentas
RUN apt-get update && apt-get install -y netcat-openbsd dos2unix

# 2) Cria e antecipa venv
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# 3) Copia requirements e instala
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 4) Copia TODO o projeto (inclusive entrypoint com CRLF)
COPY . /app

# 5) Converte finais de linha e dá permissão ao entrypoint
RUN dos2unix /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# 6) Expõe porta e define entrypoint
EXPOSE 8080
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
