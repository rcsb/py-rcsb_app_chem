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

# from rcsb.app.chem.ReloadDependencies import ReloadDependencies

from rcsb.utils.chem.ChemCompDepictWrapper import ChemCompDepictWrapper
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
        testFlagFull = False
        dataPath = os.path.join(HERE, "test-data")
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        self.__ccFileNamePrefix = "cc-abbrev"
        self.__testBuildConfiguration(self.__cachePath, dataPath, self.__ccFileNamePrefix, testFlagFull)

        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def __testBuildConfiguration(self, cachePath, dataPath, ccFileNamePrefix, testFlagFull):
        """Build bootstrap configuration
        """
        try:
            logger.info("Update configuration for prefix %r testFlagFull %r", ccFileNamePrefix, testFlagFull)
            ccsw = ChemCompSearchWrapper(cachePath=cachePath, ccFileNamePrefix=ccFileNamePrefix)
            ccUrlTarget = os.path.join(dataPath, "components-abbrev.cif") if not testFlagFull else None
            birdUrlTarget = os.path.join(dataPath, "prdcc-abbrev.cif") if not testFlagFull else None
            logger.info("Data source cc %r bird %r", ccUrlTarget, birdUrlTarget)
            ok = ccsw.setConfig(ccUrlTarget=ccUrlTarget, birdUrlTarget=birdUrlTarget)
            self.assertTrue(ok)
            #
            ccdw = ChemCompDepictWrapper()
            ok = ccdw.setConfig(cachePath)
            self.assertTrue(ok)
        except Exception as e:
            logger.exception("Failing with %s", str(e))
            self.fail()

    def testUpdateDependencies(self):
        """Test update search index.
        """
        try:
            logger.info("Updating dependences for prefix %r", self.__ccFileNamePrefix)
            ccsw = ChemCompSearchWrapper(cachePath=self.__cachePath, ccFileNamePrefix=self.__ccFileNamePrefix)
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
