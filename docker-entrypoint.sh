#!/bin/bash

echo "Current cron schedule is: ${UPDATE_CRON_SCHEDULE}"

echo "${ACCOUNT_ID}"
echo "${LICENSE_KEY}"

echo "ACCOUNT_ID=${ACCOUNT_ID}" > /etc/cron.env
echo "LICENSE_KEY=${LICENSE_KEY}" >> /etc/cron.env
echo "PATH=${PATH}" >> /etc/cron.env

chmod 644 /etc/cron.env

# setup cron job file with schedule and command
echo "${UPDATE_CRON_SCHEDULE} . /etc/cron.env; /app/update.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/updatejob

# set permissions and register it
chmod 0644 /etc/cron.d/updatejob
crontab /etc/cron.d/updatejob

# create cron log file
touch /var/log/cron.log

# start cron in background
cron

# run fastapi app
exec uvicorn server.app.main:create_app --factory --host 0.0.0.0 --port 8000