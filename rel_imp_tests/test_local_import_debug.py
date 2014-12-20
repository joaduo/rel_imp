'''

'''
import unittest
import rel_imp_tests.test_local_import
import rel_imp


class TestRelativeImport(rel_imp_tests.test_local_import.TestRelativeImport):
    _log_level = rel_imp.DEBUG

if __name__ == "__main__":
    unittest.main()
