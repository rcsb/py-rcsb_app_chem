#!/bin/bash
# File: UPDATE.sh
# Date: 28-Jun-2020
#
# Example script to locally update dependency files using default public
# chemical component and BIRD data sources.
#
# Run as:
#    nohup ./scripts/UPDATE.sh >& LOGUPDATE &
#
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
export OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
#
echo "OE_LICENSE=$OE_LICENSE"
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
#
unset CHEM_SEARCH_DATA_HOSTNAME
unset CHEM_SEARCH_DATA_PATH
#
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
export CHEM_DEPICT_CACHE_PATH=${TOPDIR}/CACHE
#
python3.8 ${TOPDIR}/rcsb/app/chem/ReloadDependencies.py
#