FROM python:3.14.4-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# mysqlclient is a native extension, so install the compiler and MySQL/MariaDB headers.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

# Render supplies PORT. Migrations run when the container starts, with runtime env vars available.
CMD ["sh", "-c", "python manage.py migrate && gunicorn mpesaapi.wsgi:application --bind 0.0.0.0:${PORT:-10000} --access-logfile - --error-logfile -"]
