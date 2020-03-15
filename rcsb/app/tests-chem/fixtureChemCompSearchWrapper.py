##
# File:    ChemCompSearchWrapperFixture.py
# Author:  J. Westbrook
# Date:    13-Mar-2020
# Version: 0.001
#
# Update:
#
#
##
"""
Fixture to prepare data dependencies for ChemCompSearchWrapper()

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

from rcsb.utils.chem import __version__
from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper
from rcsb.utils.io.MarshalUtil import MarshalUtil


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ChemCompSearchWrapperFixture(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        self.__testFlagFull = False
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        # self.__buildTypeList = ["oe-iso-smiles", "oe-smiles", "cactvs-iso-smiles", "cactvs-smiles", "inchi"]
        # Run the bootstrap configuration
        self.__mU = MarshalUtil(workPath=self.__cachePath)
        self.__testBootstrapConfig()
        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def __testBootstrapConfig(self):
        """Test read/write search configuration.
        """
        try:
            if self.__testFlagFull:
                os.environ["CHEM_SEARCH_CACHE_PATH"] = os.path.join(self.__cachePath)
                os.environ["CHEM_SEARCH_CC_PREFIX"] = "cc-full"
                ccFileNamePrefix = "cc-full"
                configDirPath = os.path.join(self.__cachePath, "config")
                configFilePath = os.path.join(configDirPath, ccFileNamePrefix + "-config.json")
                oeFileNamePrefix = "oe-full"
                ccFileNamePrefix = "cc-full"
                ccUrlTarget = None
                birdUrlTarget = None
            else:
                os.environ["CHEM_SEARCH_CACHE_PATH"] = os.path.join(self.__cachePath)
                os.environ["CHEM_SEARCH_CC_PREFIX"] = "cc-abbrev"
                ccUrlTarget = os.path.join(self.__dataPath, "components-abbrev.cif")
                birdUrlTarget = os.path.join(self.__dataPath, "prdcc-abbrev.cif")
                ccFileNamePrefix = "cc-abbrev"
                configDirPath = os.path.join(self.__cachePath, "config")
                configFilePath = os.path.join(configDirPath, ccFileNamePrefix + "-config.json")
                oeFileNamePrefix = "oe-abbrev"
            #
            molLimit = None
            useCache = False
            logSizes = False
            #
            numProc = 12
            maxProc = os.cpu_count()
            numProc = min(numProc, maxProc)
            maxChunkSize = 10
            logger.info("+++ >>> Using MAXPROC %d", numProc)
            #
            limitPerceptions = True
            quietFlag = True
            #
            fpTypeCuttoffD = {"TREE": 0.6, "MACCS": 0.9, "PATH": 0.6, "CIRCULAR": 0.6, "LINGO": 0.9}
            buildTypeList = ["oe-iso-smiles", "oe-smiles", "cactvs-iso-smiles", "cactvs-smiles", "inchi"]
            #
            oesmpKwargs = {
                "ccUrlTarget": ccUrlTarget,
                "birdUrlTarget": birdUrlTarget,
                "cachePath": self.__cachePath,
                "useCache": useCache,
                "ccFileNamePrefix": ccFileNamePrefix,
                "oeFileNamePrefix": oeFileNamePrefix,
                "limitPerceptions": limitPerceptions,
                "minCount": None,
                "maxFpResults": 50,
                "fpTypeCuttoffD": fpTypeCuttoffD,
                "buildTypeList": buildTypeList,
                "screenTypeList": None,
                "quietFlag": quietFlag,
                "numProc": numProc,
                "maxChunkSize": maxChunkSize,
                "molLimit": molLimit,
                "logSizes": logSizes,
            }
            ccsiKwargs = {
                "ccUrlTarget": ccUrlTarget,
                "birdUrlTarget": birdUrlTarget,
                "cachePath": self.__cachePath,
                "useCache": useCache,
                "ccFileNamePrefix": ccFileNamePrefix,
                "oeFileNamePrefix": oeFileNamePrefix,
                "limitPerceptions": limitPerceptions,
                "minCount": None,
                "numProc": numProc,
                "quietFlag": quietFlag,
                "maxChunkSize": maxChunkSize,
                "molLimit": None,
                "logSizes": False,
            }
            configD = {"versionNumber": 0.20, "ccsiKwargs": ccsiKwargs, "oesmpKwargs": oesmpKwargs}
            self.__mU.mkdir(configDirPath)
            self.__mU.doExport(configFilePath, configD, fmt="json", indent=3)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testUpdateDependencies(self):
        """Test update search index.
        """
        try:
            ccsw = ChemCompSearchWrapper()
            ok = ccsw.readConfig()
            self.assertTrue(ok)
            ok = ccsw.updateChemCompIndex()
            self.assertTrue(ok)
            ok = ccsw.updateSearchIndex()
            self.assertTrue(ok)
            ok = ccsw.updateSearchMoleculeProvider()
            self.assertTrue(ok)
            # verify access -
            ok = ccsw.reloadSearchDatabase()
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()


def loadDependenciesSuite():
    suiteSelect = unittest.TestSuite()
    suiteSelect.addTest(ChemCompSearchWrapperFixture("testUpdateDependencies"))
    return suiteSelect


if __name__ == "__main__":
    mySuite = loadDependenciesSuite()
    unittest.TextTestRunner(verbosity=2).run(mySuite)
