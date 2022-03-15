"""
Test local import
"""
import imp
import unittest
import rel_imp


class TestRelativeImport(unittest.TestCase):
    _log_level = rel_imp.ERROR

    def test_rimport(self):
        import rel_imp
        rel_imp.init(self._log_level)
        from .relimported1 import example_function
        example_function()

    def test_reimporting(self):
        import rel_imp
        rel_imp.init(self._log_level)
        import rel_imp
        rel_imp.init(self._log_level)

    def test_reload(self):
        import rel_imp
        rel_imp.init(self._log_level)
        rel_imp = imp.reload(rel_imp)
        rel_imp.init(self._log_level)


if __name__ == "__main__":
    unittest.main()

