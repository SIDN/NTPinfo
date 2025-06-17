# 15d/server/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server/ ./server

COPY update_geolite_and_bgptools_dbs.sh /app/update.sh
RUN chmod +x /app/update.sh

#RUN echo "0 0 * * * /app/update.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/dailyupdate && \
#    chmod 0644 /etc/cron.d/dailyupdate && \
#    crontab /etc/cron.d/dailyupdate
#
#RUN touch /var/log/cron.log
#/app/update.sh && cron &&

CMD ["uvicorn", "server.app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
