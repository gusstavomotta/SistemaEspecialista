#!/bin/bash

echo "Aguardando o Postgres..."
while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
    sleep 1
done
echo "Postgres disponível!"

source /venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec gunicorn SistemaEspecialista.wsgi:application \
      --bind 0.0.0.0:8080 \
      --workers 5 \
      --worker-class gevent \
      --timeout 30
