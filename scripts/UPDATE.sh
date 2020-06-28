#!/bin/bash
#
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOPDIR="$(dirname "$HERE")"
export OE_LICENSE=${OE_LICENSE:=~/oe_license.txt}
#
echo "OE_LICENSE=$OE_LICENSE"
echo "HERE=${HERE}"
echo "TOPDIR=${TOPDIR}"
#
export CHEM_SEARCH_CC_PREFIX="cc-full"
export CHEM_SEARCH_CACHE_PATH=${TOPDIR}/CACHE
#
python3.8 ${TOPDIR}/rcsb/app/chem/ReloadDependencies.py
#