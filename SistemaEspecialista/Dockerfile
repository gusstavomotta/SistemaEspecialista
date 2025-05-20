FROM python:latest

# 1) Instala ferramentas
RUN apt-get update && apt-get install -y netcat-openbsd dos2unix

# 2) Cria ambiente virtual e configura PATH
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# 3) Copia requirements e instala dependências
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 4) Copia tudo do projeto (incluindo o entrypoint.sh)
COPY . /app

# 5) Converte finais de linha e dá permissão ao entrypoint
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# (Opcional) Executa collectstatic na build – lembre-se do volume: se o volume for montado,
# os arquivos gerados aqui podem ser sobrescritos; por isso, é recomendado executar isso no entrypoint.
RUN python manage.py collectstatic --noinput --clear

# 6) Expõe a porta que o Gunicorn utiliza
EXPOSE 8080

# 7) Define o entrypoint
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
