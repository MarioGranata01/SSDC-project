FROM python:3.11-slim

WORKDIR /app
COPY handler.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "handler.py"]
