#!/bin/bash

echo "Aguardando o Postgres..."
while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
    sleep 1
done
echo "Postgres disponível!"

# Ativa o ambiente virtual
source /venv/bin/activate

# Instala as dependências, caso necessário
pip install -r requirements.txt

# Cria e aplica migrações
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# (Re)gera os arquivos estáticos; importante executar após o volume ser montado
python manage.py collectstatic --noinput

# Inicia o Gunicorn, substituindo o runserver; 
# ajuste "sistemaespecialista" conforme a estrutura do seu projeto.
exec gunicorn SistemaEspecialista.wsgi:application --bind 0.0.0.0:8080 --workers 3
