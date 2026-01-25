# Imagen base liviana y estable
FROM python:3.12-slim

# Variables recomendadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copiamos requirements primero (mejor cache)
COPY requirements.txt .

# Instalamos dependencias Python
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copiamos el código
COPY . .

# Puerto FastAPI
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
