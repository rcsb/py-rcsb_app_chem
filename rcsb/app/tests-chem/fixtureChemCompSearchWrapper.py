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

from rcsb.app.chem import __version__
from rcsb.app.chem.ReloadDependencies import ReloadDependencies

from rcsb.utils.chem.ChemCompSearchWrapper import ChemCompSearchWrapper


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ChemCompSearchWrapperFixture(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        self.__testFlagFull = os.environ.get("CHEM_SEARCH_CC_PREFIX", "cc-abbrev") == "cc-full"
        self.__workPath = os.path.join(HERE, "test-output")
        self.__dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        self.__ccFileNamePrefix = "cc-abbrev"
        rdp = ReloadDependencies(cachePath=self.__cachePath, ccFileNamePrefix=self.__ccFileNamePrefix)
        rdp.shutdown()
        # rdp.updateDependencies()

        # self.__buildTypeList = ["oe-iso-smiles", "oe-smiles", "cactvs-iso-smiles", "cactvs-smiles", "inchi"]
        # Run the bootstrap configuration
        # self.__mU = MarshalUtil(workPath=self.__cachePath)
        # self.__makeBootstrapDepictConfig(self.__testFlagFull)
        # self.__testBootstrapConfig()

        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

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
