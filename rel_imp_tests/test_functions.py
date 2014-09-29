'''

'''
import unittest
from rel_imp import _print_exc, _get_search_path, _solve_pkg, _try_search_paths
from os import path
import sys
if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


class TestRelativeImport(unittest.TestCase):
    def test_functions(self):
        stderr = sys.stderr 
        sys.stderr = StringIO()
        _print_exc(Exception('Example'))
        _try_search_paths(globals())
        main_file_dir = path.dirname(path.abspath(__file__))
        _get_search_path(main_file_dir, sys.path)
        main_globals = dict(__file__=__file__)
        pkg = _solve_pkg(main_globals)
        self.assertEqual(pkg, 'rel_imp_tests')
        self.assertTrue(pkg in sys.modules)
        err = sys.stderr
        value = ("Exception enabling relative_import for __main__. Ignoring it:"
                   " Exception('Example',)\n  relative_import won't be enabled.\n")
        self.assertEqual(err.getvalue(), value)
        sys.stderr = stderr

if __name__ == "__main__":
    unittest.main()
