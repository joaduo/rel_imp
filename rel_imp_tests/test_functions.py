'''

'''
import unittest
from rel_imp import __print_exc, __get_search_path, __solve_pkg
from os import path
import sys

class TestRelativeImport(unittest.TestCase):
    def test_functions(self):
        g = globals()
        g.get('__print_exc')(Exception('Example'))
        main_file_dir = path.dirname(path.abspath(__file__))
        g.get('__get_search_path')(main_file_dir, sys.path)
        main_globals = dict(__file__=__file__)
        pkg = g.get('__solve_pkg')(main_globals)
        self.assertEqual(pkg, 'rel_imp_tests')
        self.assertTrue(pkg in sys.modules)
        
        
if __name__ == "__main__":
    unittest.main()
