#!/bin/bash
# File:  LAUNCH.sh
# Date:  28-Jun-2020

# App module template covention is - rcsb.app.<service_name>.main:app
SERVICE_NAME=${SERVICE_NAME:-"chem"}
export APP_MODULE="rcsb.app.${SERVICE_NAME}.main:app"
export GUNICORN_CONF=${GUNICORN_CONF:-"/app/gunicorn_conf.py"}
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

# Optional setup.sh
SETUP_PATH=${SETUP_PATH:-/app/setup.sh}
echo "Checking for setup script in $SETUP_PATH"
if [ -f $SETUP_PATH ] ; then
    echo "Running setup script $SETUP_PATH"
    . "$SETUP_PATH"
else
    echo "There is no setup script $SETUP_PATH"
fi

# Start Gunicorn
echo "Worker class is $WORKER_CLASS"
echo "Gunicorn config is $GUNICORN_CONF"
echo "Application module is $APP_MODULE"
#
cd /app
exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"