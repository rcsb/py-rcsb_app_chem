#!/bin/bash
# Date: 28-Jun-2020
# Example deployment using gunicorn server
#
# Run as:
#
#     nohup ./scripts/LAUNCH_GUNICORN.sh >& LOGTODAY
##
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
echo "OE_LICENSE=$OE_LICENSE"

THISIP=${HOSTIP:="0.0.0.0"}
THISPORT=${HOSTPORT:="8000"}
ADDR=${THISIP}:${THISPORT}

unset CHEM_SEARCH_DATA_HOSTNAME
unset CHEM_SEARCH_DATA_PATH
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${HERE}/CACHE
export CHEM_DEPICT_CACHE_PATH=${HERE}/CACHE
export GIT_PYTHON_REFRESH=quiet

gunicorn \
rcsb.app.chem.main:app \
    --timeout 300 \
    --chdir ${HERE} \
    --bind ${ADDR} \
    --reload \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
