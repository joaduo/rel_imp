"""
Test global import debug.
"""
import unittest

import rel_imp

rel_imp.init(log_level=rel_imp.DEBUG)
import rel_imp_tests.test_global_import


class TestRelativeImportDebug(rel_imp_tests.test_global_import.TestRelativeImport):
    pass


if __name__ == "__main__":
    unittest.main()
