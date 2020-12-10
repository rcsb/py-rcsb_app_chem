##
# File:    testConvertTools.py
# Author:  J. Westbrook
# Date:    10-Dec-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for descriptor and chemical componen conversion api.

"""

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

import logging
import os
import platform
import resource
import time
import unittest

from fastapi.testclient import TestClient
from rcsb.app.chem import __version__
from rcsb.app.chem.main import app

HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ConvertToolsTests(unittest.TestCase):
    def setUp(self):
        self.__testFlagFull = False
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        os.environ["CHEM_DEPICT_CACHE_PATH"] = os.path.join(self.__cachePath)
        os.environ["CHEM_SEARCH_CACHE_PATH"] = os.path.join(self.__cachePath)
        os.environ["CHEM_SEARCH_CC_PREFIX"] = "cc-full" if self.__testFlagFull else "cc-abbrev"
        self.__client = TestClient(app)
        self.__startTime = time.time()
        #
        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testOne(self):
        """Get root path (service alive example)."""
        try:
            with TestClient(app) as client:
                response = client.get("/")
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                self.assertTrue(response.json() == {"msg": "Service is up!"})
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testToMolFilePost(self):
        try:
            smi = "CC[C@H](C)[C@@H](C(=O)N[C@@H](CC(C)C)C(=O)O)NC(=O)[C@H](Cc1ccccc1)CC(=O)NO"
            with TestClient(app) as client:
                response = client.post(
                    "/chem-convert-v1/to-molfile/SMILES",
                    json={"target": smi, "fmt": "mol"},
                )
                logger.info("Response status %r", response.status_code)
                self.assertTrue(response.status_code == 200)
                logger.debug("Response info %r ", dir(response))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testToMolFileGet(self):
        try:
            smi = "CC[C@H](C)[C@@H](C(=O)N[C@@H](CC(C)C)C(=O)O)NC(=O)[C@H](Cc1ccccc1)CC(=O)NO"
            with TestClient(app) as client:
                response = client.get("/chem-convert-v1/to-molfile/SMILES", params={"target": smi})
                logger.info("Response status %r", response.status_code)
                self.assertTrue(response.status_code == 200)
                logger.debug("Response info %r ", dir(response))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testToMolFileIdentifierGet(self):
        try:
            pdbId = "001"
            with TestClient(app) as client:
                response = client.get("/chem-convert-v1/to-molfile/IdentifierPDB", params={"target": pdbId})
                logger.info("Response status %r", response.status_code)
                self.assertTrue(response.status_code == 200)
                logger.debug("Response info %r ", dir(response))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testToMolFileIdentifierPost(self):
        try:
            pdbId = "002"
            with TestClient(app) as client:
                response = client.post(
                    "/chem-convert-v1/to-molfile/IdentifierPDB",
                    json={"target": pdbId, "fmt": "sdf"},
                )
                logger.info("Response status %r", response.status_code)
                self.assertTrue(response.status_code == 200)
                logger.debug("Response info %r ", dir(response))
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def apiSimpleTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ConvertToolsTests("testToMolFilePost"))
    suiteSelect.addTest(ConvertToolsTests("testToMolFileGet"))
    suiteSelect.addTest(ConvertToolsTests("testToMolFileIdentifierGet"))
    suiteSelect.addTest(ConvertToolsTests("testToMolFileIdentifierPost"))
    return suiteSelect


if __name__ == "__main__":

    mySuite = apiSimpleTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
