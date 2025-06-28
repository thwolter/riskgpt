import sys
import unittest

# Import the test classes
from tests.unit.test_search_improvements import (
    TestContextualWikipedia,
    TestDeduplication,
    TestParallelExecution,
    TestRanking,
)


# Create a test suite
def create_test_suite():
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(TestDeduplication))
    suite.addTest(unittest.makeSuite(TestRanking))
    suite.addTest(unittest.makeSuite(TestContextualWikipedia))
    suite.addTest(unittest.makeSuite(TestParallelExecution))

    return suite


if __name__ == "__main__":
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(create_test_suite())

    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())
