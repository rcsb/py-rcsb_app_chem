##
# File:    testMatchFormula.py
# Author:  J. Westbrook
# Date:    9-Mar-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for formula matching api.

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


class MatchFormulaTests(unittest.TestCase):
    def setUp(self):
        self.__testFlagFull = False
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        os.environ["CHEM_SEARCH_CACHE_PATH"] = os.path.join(self.__cachePath)
        os.environ["CHEM_DEPICT_CACHE_PATH"] = os.path.join(self.__cachePath)
        os.environ["CHEM_SEARCH_CC_PREFIX"] = "cc-full" if self.__testFlagFull else "cc-abbrev"

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

    def testRoot(self):
        """ Get root path (service alice example).
        """
        try:
            with TestClient(app) as client:
                response = client.get("/")
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                self.assertTrue(response.json() == {"msg": "Service is up!"})
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testMatchRangePost(self):
        try:
            fQ = {"O": {"min": 1, "max": 5}, "C": {"min": 6, "max": 15}, "H": {"min": 5, "max": 20}}
            matchSubset = True
            with TestClient(app) as client:
                response = client.post("/chem-match-v1/formula/range", json={"query": fQ, "matchSubset": matchSubset})
                logger.info("Status %r response %s", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                rD = response.json()
                self.assertTrue(rD["query"], fQ)
                self.assertTrue(len(rD["matchedIdList"]) > 0)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testMatchGet(self):
        try:
            fS = "C23H35N3O6"
            matchSubset = True
            with TestClient(app) as client:
                response = client.get("/chem-match-v1/formula", params={"query": fS, "matchSubset": matchSubset})
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                rD = response.json()
                self.assertTrue(rD["query"], fS)
                self.assertTrue(len(rD["matchedIdList"]) > 0)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testMatchPost(self):
        try:
            fS = "C23H35N3O6"
            matchSubset = True
            fQ = {"query": fS, "matchSubset": matchSubset}
            with TestClient(app) as client:
                response = client.post("/chem-match-v1/formula", json={"query": fS, "matchSubset": matchSubset})
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                rD = response.json()
                self.assertTrue(rD["query"], fQ)
                self.assertTrue(len(rD["matchedIdList"]) > 0)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def apiSimpleTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MatchFormulaTests("testMatchRangePost"))
    suiteSelect.addTest(MatchFormulaTests("testMatchGet"))
    suiteSelect.addTest(MatchFormulaTests("testMatchPost"))
    return suiteSelect


if __name__ == "__main__":

    mySuite = apiSimpleTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
