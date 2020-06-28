##
# File: main.py
# Date: 12-Mar-2020
#
##
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "john.westbrook@rcsb.org"
__license__ = "Apache 2.0"

import logging
import os

from fastapi import FastAPI

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper
from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

from . import depictTools
from . import descriptorMatch
from . import formulaMatch
from . import serverStatus

# ---
logger = logging.getLogger("app_chem")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:     %(asctime)s-%(module)s.%(funcName)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
# ---

app = FastAPI()


@app.on_event("startup")
async def startupEvent():
    logger.info("Startup - loading search dependencies")
    ccsw = ChemCompSearchWrapper()
    #
    clDataUrl = os.environ.get("CHEM_SEARCH_DATA_HOSTNAME", None)
    clDataPath = os.environ.get("CHEM_SEARCH_DATA_PATH", None)
    clChannel = os.environ.get("CHEM_SEARCH_UPDATE_CHANNEL", None)
    #
    logger.info("Dependence data host %r path %r update channel %r", clDataUrl, clDataPath, clChannel)
    if clDataUrl and clDataPath and clChannel in ["A", "B", "a", "b"]:
        ccsw.restoreDependencies("http://" + clDataUrl, clDataPath, bundleLabel=clChannel.upper())
    #
    ok1 = ccsw.readConfig()
    ok2 = ccsw.updateChemCompIndex(useCache=True)
    ok3 = ccsw.reloadSearchDatabase()
    #
    logger.info("Completed - loading search dependencies status %r", ok1 and ok2 and ok3)
    ccdw = ChemCompDepictWrapper()
    ok1 = ccdw.readConfig()
    logger.info("Completed - loading depict dependencies status %r", ok1)
    #


@app.on_event("shutdown")
def shutdownEvent():
    logger.info("Shutdown - application ended")


app.include_router(
    formulaMatch.router, prefix="/chem-match-v1",
)

app.include_router(
    descriptorMatch.router, prefix="/chem-match-v1",
)

app.include_router(
    depictTools.router, prefix="/chem-depict-v1",
)

app.include_router(serverStatus.router)
