'''

'''
import unittest

class TestRelativeImport(unittest.TestCase):
    def test_rimport(self):
        import relative_import
        from .relimported1 import example_function
        example_function()
        
    def test_reimporting(self):
        import relative_import
        import relative_import
        
    def test_reload(self):
        import relative_import
        relative_import = reload(relative_import)

if __name__ == "__main__":
    unittest.main()
