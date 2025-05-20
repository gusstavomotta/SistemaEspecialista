FROM python:latest

RUN apt-get update && apt-get install -y netcat-openbsd dos2unix

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh


RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
