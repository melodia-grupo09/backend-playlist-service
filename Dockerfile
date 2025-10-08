# Imagen base
FROM python:3.11-slim

# Evita que Python guarde .pyc y active buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer el puerto
EXPOSE ${PORT}

# Comando de inicio
CMD ["sh", "-c", "uvicorn app.main:app --host $HOST --port $PORT"]
