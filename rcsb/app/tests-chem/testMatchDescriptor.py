##
# File:    testMatchDescriptor.py
# Author:  J. Westbrook
# Date:    9-Mar-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Tests for descriptor matching api.

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


class MatchDescriptorTests(unittest.TestCase):
    def setUp(self):
        self.__testFlagFull = False
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")

        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        os.environ["CHEM_SEARCH_CACHE_PATH"] = os.path.join(self.__cachePath)
        os.environ["CHEM_DEPICT_CACHE_PATH"] = os.path.join(self.__cachePath)
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
        """ Get root path (service alive example).
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

    def testMatchPost(self):
        try:
            smi = "CC[C@H](C)[C@@H](C(=O)N[C@@H](CC(C)C)C(=O)O)NC(=O)[C@H](Cc1ccccc1)CC(=O)NO"
            with TestClient(app) as client:
                response = client.post("/chem-match-v1/SMILES", json={"query": smi, "matchType": "graph-relaxed", "generator": "ME"},)
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                rD = response.json()
                self.assertTrue(rD["descriptorType"], "SMILES")
                self.assertTrue(rD["query"], smi)
                self.assertTrue(len(rD["matchedIdList"]) > 0)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testMatchGet(self):
        try:
            smi = "CC[C@H](C)[C@@H](C(=O)N[C@@H](CC(C)C)C(=O)O)NC(=O)[C@H](Cc1ccccc1)CC(=O)NO"
            with TestClient(app) as client:
                response = client.get("/chem-match-v1/SMILES", params={"query": smi, "matchType": "graph-relaxed", "generator": "ME"})
                logger.info("Status %r response %r", response.status_code, response.json())
                self.assertTrue(response.status_code == 200)
                rD = response.json()
                self.assertTrue(rD["descriptorType"], "SMILES")
                self.assertTrue(rD["query"], smi)
                self.assertTrue(len(rD["matchedIdList"]) > 0)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def apiSimpleTests():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(MatchDescriptorTests("testMatchPost"))
    suiteSelect.addTest(MatchDescriptorTests("testMatchGet"))
    return suiteSelect


if __name__ == "__main__":

    mySuite = apiSimpleTests()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
