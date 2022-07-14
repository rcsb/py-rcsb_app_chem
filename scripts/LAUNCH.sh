#!/bin/bash
# File:  LAUNCH.sh
# Date:  28-Jun-2020
#
# Example uvicorn deployment on non-privileged port.
#
#   nohup ./scripts/LAUNCH.sh >& LOGLAUNCH
##
# HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# TOPDIR="$(dirname "$HERE")"
# OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
# echo "HERE=${HERE}"
# echo "TOPDIR=${TOPDIR}"
# echo "OE_LICENSE=$OE_LICENSE"
# #

# THISIP=${HOSTIP:="127.0.0.1"}
# THISPORT=${HOSTPORT:="8000"}
# #
# unset CHEM_SEARCH_DATA_HOSTNAME
# unset CHEM_SEARCH_DATA_PATH
# export CHEM_SEARCH_CC_PREFIX="cc-full"
# export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
# export CHEM_DEPICT_CACHE_PATH=${TOPDIR}/CACHE
# #
# cd ${TOPDIR}
# python3 -m uvicorn --host ${THISIP} --port ${THISPORT} --reload rcsb.app.chem.main:app


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