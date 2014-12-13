'''

'''
import unittest
import rel_imp; rel_imp.init(log_level=rel_imp.DEBUG)
from ..relimported1 import example_function

class TestRelativeImport(unittest.TestCase):
    def test_rimport(self):
        example_function()
        from ..relimported2 import example_function as ex2
        ex2()

if __name__ == "__main__":
    unittest.main()
