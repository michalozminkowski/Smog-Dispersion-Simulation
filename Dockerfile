FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libspatialindex-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/app
ENV DOCKER_ENV=True

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]