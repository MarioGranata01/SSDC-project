# Dockerfile per il container di training
FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Copia i file necessari
COPY handler.py .
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Comando di default per eseguire il container
CMD ["python", "handler.py"]
