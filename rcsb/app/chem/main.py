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
from fastapi.middleware.cors import CORSMiddleware

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper
from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper

from . import convertTools
from . import depictTools
from . import descriptorMatch
from . import formulaMatch
from . import LogFilterUtils
from . import serverStatus

#
# ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
# The following mimics the default Gunicorn logging format
formatter = logging.Formatter("%(asctime)s [%(process)d] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s", "[%Y-%m-%d %H:%M:%S %z]")
# The following mimics the default Uvicorn logging format
# formatter = logging.Formatter("%(levelname)s:     %(asctime)s-%(module)s.%(funcName)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = True
# Apply logging filters -
lu = LogFilterUtils.LogFilterUtils()
lu.addFilters()
# ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# http --verbose OPTIONS :8000/status  Access-Control-Request-Method:GET Origin:https://id-localtest.mydomain.co


def restoreSearchDependencies(ccsw):
    """Fetch this service path's search dependency bundle from remote storage and unpack it in the local cache.

    The source is selected from the environment:

        CHEM_SEARCH_STASH_URL, CHEM_SEARCH_STASH_PATH: S3/MinIO stash written by the weekly-update etl-chem
            workflow (e.g. s3://wuw-data-stash and /a); endpoint and credentials come from the standard
            AWS_ENDPOINT_URL, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables.
        CHEM_SEARCH_DATA_HOSTNAME, CHEM_SEARCH_DATA_PATH: legacy HTTP source (BuildLocker), used only when
            CHEM_SEARCH_STASH_URL isn't set.
        CHEM_SEARCH_UPDATE_CHANNEL: A or B, the bundle label for this service path.

    If no source is configured, the existing local cache is used as is.

    Raises:
        RuntimeError: a source is configured but incomplete, or the bundle can't be restored.
    """
    clChannel = os.environ.get("CHEM_SEARCH_UPDATE_CHANNEL", None)
    stashUrl = os.environ.get("CHEM_SEARCH_STASH_URL", None)
    if stashUrl:
        dataUrl = stashUrl
        dataPath = os.environ.get("CHEM_SEARCH_STASH_PATH", None)
    else:
        dataHost = os.environ.get("CHEM_SEARCH_DATA_HOSTNAME", None)
        dataUrl = "http://" + dataHost if dataHost else None
        dataPath = os.environ.get("CHEM_SEARCH_DATA_PATH", None)
    #
    logger.info("Dependency data url %r path %r update channel %r", dataUrl, dataPath, clChannel)
    if not dataUrl:
        logger.info("No remote dependency data configured - using the local cache")
        return
    if not dataPath or not clChannel or clChannel.upper() not in ["A", "B"]:
        raise RuntimeError("Incomplete remote dependency settings: url %r path %r update channel %r" % (dataUrl, dataPath, clChannel))
    ok = ccsw.restoreDependencies(dataUrl, dataPath, bundleLabel=clChannel.upper())
    if not ok:
        raise RuntimeError("Failed to restore search dependencies from url %r path %r update channel %r" % (dataUrl, dataPath, clChannel))
    logger.info("Restored search dependencies from url %r path %r update channel %r", dataUrl, dataPath, clChannel)


@app.on_event("startup")
async def startupEvent():
    logger.info("Startup - loading search dependencies")
    #
    ccsw = ChemCompSearchWrapper()
    restoreSearchDependencies(ccsw)
    #
    ok1 = ccsw.readConfig()
    ok2 = ccsw.updateChemCompIndex(useCache=True)
    ok3 = ccsw.reloadSearchDatabase()
    ok4 = ccsw.updateSearchIndex(useCache=True)
    #
    logger.info("Completed - loading search dependencies status %r", ok1 and ok2 and ok3 and ok4)
    ccdw = ChemCompDepictWrapper()
    ok1 = ccdw.readConfig()
    logger.info("Completed - loading depict dependencies status %r", ok1)
    #
    ccsw.status()
    #


@app.on_event("shutdown")
def shutdownEvent():
    logger.info("Shutdown - application ended")


app.include_router(
    formulaMatch.router,
    prefix="/chem-match-v1",
)

app.include_router(
    descriptorMatch.router,
    prefix="/chem-match-v1",
)

app.include_router(
    depictTools.router,
    prefix="/chem-depict-v1",
)

app.include_router(
    convertTools.router,
    prefix="/chem-convert-v1",
)

app.include_router(serverStatus.router)
