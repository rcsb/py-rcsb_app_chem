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


HERE = os.path.abspath(os.path.dirname(__file__))
TOPDIR = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]-%(module)s.%(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ChemCompSearchWrapperFixture(unittest.TestCase):
    def setUp(self):
        self.__startTime = time.time()
        configFlagFull = False
        self.__cachePath = os.path.join(HERE, "test-output", "CACHE")
        dataPath = os.path.join(HERE, "test-data")
        if not configFlagFull:
            self.__ccFileNamePrefix = "cc-abbrev"
            ccUrlTarget = os.path.join(dataPath, "components-abbrev.cif") if not configFlagFull else None
            birdUrlTarget = os.path.join(dataPath, "prdcc-abbrev.cif") if not configFlagFull else None
        else:
            self.__ccFileNamePrefix = "cc-full"
            ccUrlTarget = birdUrlTarget = None

        rD = ReloadDependencies(self.__cachePath, self.__ccFileNamePrefix)
        rD.buildConfiguration(ccUrlTarget=ccUrlTarget, birdUrlTarget=birdUrlTarget)
        rD.shutdown()
        #
        logger.debug("Running tests on version %s", __version__)
        logger.info("Starting %s at %s", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

    def tearDown(self):
        unitS = "MB" if platform.system() == "Darwin" else "GB"
        rusageMax = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        logger.info("Maximum resident memory size %.4f %s", rusageMax / 10 ** 6, unitS)
        endTime = time.time()
        logger.info("Completed %s at %s (%.4f seconds)", self.id(), time.strftime("%Y %m %d %H:%M:%S", time.localtime()), endTime - self.__startTime)

    def testUpdateDependencies(self):
        """Test update search indices.
        """
        try:
            rD = ReloadDependencies(self.__cachePath, self.__ccFileNamePrefix)
            ok = rD.updateDependencies()
            self.assertTrue(ok)
            rD.shutdown()
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
