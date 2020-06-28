#!/bin/bash
# File:  LAUNCH.sh
# Date:  28-Jun-2020
#
# Example uvicorn deployment on non-privileged port.
#
#   nohup ./scripts/LAUNCH.sh >& LOGLAUNCH
##
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
echo "OE_LICENSE=$OE_LICENSE"
#

THISIP=${HOSTIP:="127.0.0.1"}
THISPORT=${HOSTPORT:="8000"}
#
unset CHEM_SEARCH_DATA_HOSTNAME
unset CHEM_SEARCH_DATA_PATH
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
export CHEM_DEPICT_CACHE_PATH=${TOPDIR}/CACHE
#
cd ${TOPDIR}
python3.8 -m uvicorn --host ${THISIP} --port ${THISPORT} --reload rcsb.app.chem.main:app