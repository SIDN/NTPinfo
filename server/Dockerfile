# 15d/server/Dockerfile
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

COPY update_geolite_and_bgptools_dbs.sh /app/update.sh
RUN chmod +x /app/update.sh

RUN echo "0 0 * * * /app/update.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/dailyupdate && \
    chmod 0644 /etc/cron.d/dailyupdate && \
    crontab /etc/cron.d/dailyupdate

RUN touch /var/log/cron.log

CMD bash -c "/app/update.sh && cron && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"
