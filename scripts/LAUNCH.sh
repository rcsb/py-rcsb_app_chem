#!/bin/bash
#
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
#
THISIP=${HOSTIP:="127.0.0.1"}
THISPORT=${HOSTPOST:="8000"}
#
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
#
cd ${TOPDIR}
python3.8 -m uvicorn --host ${THISIP} --port ${THISPORT} --reload rcsb.app.chem.main:app