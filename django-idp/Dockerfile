FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Permisos del entrypoint
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# DEV (runserver). Para PROD cambia a gunicorn (abajo).
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# PROD ejemplo:
# CMD ["gunicorn", "project.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "2", "--threads", "4"]
