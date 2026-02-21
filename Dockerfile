FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN printf '#!/bin/sh\n\
echo "Esperando a PostgreSQL..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.5\n\
done\n\
echo "PostgreSQL listo."\n\
echo "Aplicando migraciones..."\n\
python manage.py migrate --noinput\n\
echo "Recopilando archivos estaticos..."\n\
python manage.py collectstatic --noinput\n\
echo "Iniciando servidor..."\n\
exec "$@"\n' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]