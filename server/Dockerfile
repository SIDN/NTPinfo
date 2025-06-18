# 15d/server/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev gcc cron curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server/ ./server

COPY update.sh /app/update.sh
RUN chmod +x /app/update.sh

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

#CMD ["uvicorn", "server.app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["/app/docker-entrypoint.sh"]
