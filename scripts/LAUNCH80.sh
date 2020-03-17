#!/bin/bash
#
#  Run as:
#  sudo export OE_LICENSE=/home/ubuntu/oe_license.txt; nohup ./scripts/LAUNCH80.sh >& LOGTODAY
#
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
export OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
echo "OE_LICENSE=$OE_LICENSE"
#
THISIP=0.0.0.0
THISPORT=80
#
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
#
cd ${TOPDIR}
python3.8 -m uvicorn --workers 1 --host ${THISIP} --port ${THISPORT} --reload --forwarded-allow-ips 0.0.0.0 rcsb.app.chem.main:app