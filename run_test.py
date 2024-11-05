# -*- coding: utf-8 -*-
# =============================================================================
# This file is part of WaterGAP.

# WaterGAP is an opensource software which computes water flows and storages as
# well as water withdrawals and consumptive uses on all continents.

# You should have received a copy of the LGPLv3 License along with WaterGAP.
# if not see <https://www.gnu.org/licenses/lgpl-3.0>
# =============================================================================
"""Run all tests in the 'test' directory."""

import unittest
import os

def run_all_tests():
    """Run all test scripts in the 'test' directory."""
    # Find the absolute path to the test directory
    test_dir = os.path.join(os.path.dirname(__file__), 'test')

    # Load all test scripts that match 'test_*.py' pattern in 'test' directory
    loader = unittest.TestLoader()
    # Reference the test directory
    suite = loader.discover(start_dir=test_dir, pattern='test_*.py')

    # Run the tests with detailed output (verbosity level 2)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Check if all tests passed
    if result.wasSuccessful():
        print("All tests passed!")
    else:
        # Print the number of failed tests and errors
        print(f"{len(result.failures)} tests failed.")
        print(f"{len(result.errors)} tests encountered errors.")
        # Optionally exit the process with an error code if tests failed
        exit(1)


if __name__ == '__main__':
    run_all_tests()
