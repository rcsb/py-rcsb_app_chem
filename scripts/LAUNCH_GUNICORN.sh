#!/bin/bash
# Date: 28-Jun-2020
# Example deployment using gunicorn server
#
# Run as:
#
#     nohup ./scripts/LAUNCH_GUNICORN.sh >& LOGTODAY
##
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "HERE=${HERE}"

export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${HERE}/CACHE
export CHEM_DEPICT_CACHE_PATH=${HERE}/CACHE
export GIT_PYTHON_REFRESH=quiet

if grep -q docker /proc/1/cgroup; then 
    echo "inside docker container"
    THISIP=${HOSTIP:="0.0.0.0"}
else
    echo "on openstack host"
    THISIP=${HOSTIP:="127.0.0.1"}
fi
THISPORT=${HOSTPORT:="8000"}
ADDR=${THISIP}:${THISPORT}

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
