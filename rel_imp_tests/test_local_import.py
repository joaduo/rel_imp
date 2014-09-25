'''

'''
import unittest
import imp

class TestRelativeImport(unittest.TestCase):
    def test_rimport(self):
        import rel_imp; rel_imp.init()
        from .relimported1 import example_function
        example_function()
        
    def test_reimporting(self):
        import rel_imp; rel_imp.init()
        import rel_imp; rel_imp.init()
        
    def test_reload(self):
        import rel_imp; rel_imp.init()
        rel_imp = imp.reload(rel_imp)

if __name__ == "__main__":
    unittest.main()
