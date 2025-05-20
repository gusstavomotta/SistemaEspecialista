#!/bin/bash

# Espera até o banco de dados estar disponível
echo "Aguardando o Postgres..."
while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
    sleep 1
done
echo "Postgres disponível!"

# Ativa o ambiente virtual
source /venv/bin/activate

# Instala as dependências (caso não tenham sido instaladas na build)
pip install -r requirements.txt

# Cria migrações e as aplica automaticamente (sem interação)
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Inicia o servidor Django na porta 8080
exec python manage.py runserver 0.0.0.0:8080
