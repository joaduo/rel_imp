'''
Unit tests for rel_imp internals.

Unlike the other tests in this package (which only work when run as __main__),
these tests exercise rel_imp by faking __main__'s globals through exec(),
so they also run under unittest/pytest discovery.
'''
import os
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from os import path
from unittest import mock

import rel_imp
from rel_imp import (
    _get_search_path,
    _log_debug,
    _log_error,
    _solve_pkg,
    _try_search_paths,
)

REPO_ROOT = path.dirname(path.dirname(path.abspath(__file__)))
TESTS_PKG = 'rel_imp_tests'


def fake_main_env(filename='fake_main.py'):
    '''Globals dict simulating a __main__ module inside the tests package.'''
    return {
        '__name__': '__main__',
        '__file__': path.join(REPO_ROOT, TESTS_PKG, filename),
    }


class TestGetSearchPath(unittest.TestCase):

    def test_picks_closest_parent(self):
        main_dir = path.join('/a', 'b', 'pkg')
        sys_path = ['/a', path.join('/a', 'b'), main_dir, '/other']
        self.assertEqual(path.join('/a', 'b'),
                         _get_search_path(main_dir, sys_path))

    def test_excludes_main_dir(self):
        main_dir = path.join('/a', 'b')
        self.assertIsNone(_get_search_path(main_dir, [main_dir]))

    def test_no_match_returns_none(self):
        self.assertIsNone(_get_search_path(path.join('/x', 'y'),
                                           ['/unrelated']))

    def test_string_prefix_is_not_path_parent(self):
        # Regression test: os.path.commonprefix compares raw strings, so it
        # wrongly matched '/a/bar' as parent of '/a/barbaz'. commonpath does
        # not have this problem.
        main_dir = path.join('/a', 'barbaz')
        sys_path = ['/a', path.join('/a', 'bar')]
        self.assertEqual('/a', _get_search_path(main_dir, sys_path))


class TestLogging(unittest.TestCase):

    def setUp(self):
        self.addCleanup(setattr, rel_imp, '_log_level', rel_imp._log_level)

    def test_error_logged_at_default_level(self):
        rel_imp._log_level = rel_imp.ERROR
        buf = StringIO()
        with redirect_stderr(buf):
            _log_error('an error')
            _log_debug('a debug message')
        out = buf.getvalue()
        self.assertIn('an error', out)
        self.assertNotIn('a debug message', out)

    def test_debug_logged_at_debug_level(self):
        rel_imp._log_level = rel_imp.DEBUG
        buf = StringIO()
        with redirect_stderr(buf):
            _log_debug('a debug message')
        self.assertIn('a debug message', buf.getvalue())

    def test_error_silenced_above_threshold(self):
        rel_imp._log_level = rel_imp.ERROR + 10
        buf = StringIO()
        with redirect_stderr(buf):
            _log_error('an error')
        self.assertNotIn('an error', buf.getvalue())

    def test_trace_prints_stack(self):
        rel_imp._log_level = rel_imp.TRACE
        buf = StringIO()
        with redirect_stderr(buf):
            _log_debug('a debug message')
        out = buf.getvalue()
        self.assertIn('a debug message', out)
        # TRACE level also dumps the stack
        self.assertIn('test_trace_prints_stack', out)


class RelImpTestCase(unittest.TestCase):
    '''Base case handling rel_imp global state restoration.'''

    def setUp(self):
        self.addCleanup(setattr, rel_imp, '_initialized', rel_imp._initialized)
        self.addCleanup(setattr, rel_imp, '_log_level', rel_imp._log_level)
        rel_imp._initialized = False
        # make sure the tests package is importable
        if REPO_ROOT not in sys.path:
            sys.path.insert(0, REPO_ROOT)
            self.addCleanup(sys.path.remove, REPO_ROOT)
        # never let the disable var leak between tests
        old = os.environ.pop('PYTHON_DISABLE_REL_IMP', None)
        if old is not None:
            self.addCleanup(os.environ.__setitem__,
                            'PYTHON_DISABLE_REL_IMP', old)


class TestInit(RelImpTestCase):

    def test_init_sets_package(self):
        env = fake_main_env()
        exec('import rel_imp; rel_imp.init()', env)
        self.assertEqual(TESTS_PKG, env['__package__'])

    def test_init_is_idempotent(self):
        env = fake_main_env()
        exec('import rel_imp; rel_imp.init()', env)
        self.assertTrue(rel_imp._initialized)
        # a second call must do nothing
        env2 = fake_main_env('other_main.py')
        exec('import rel_imp; rel_imp.init()', env2)
        self.assertNotIn('__package__', env2)

    def test_init_disabled_by_env_var(self):
        os.environ['PYTHON_DISABLE_REL_IMP'] = '1'
        self.addCleanup(os.environ.pop, 'PYTHON_DISABLE_REL_IMP')
        env = fake_main_env()
        exec('import rel_imp; rel_imp.init()', env)
        self.assertNotIn('__package__', env)
        # not marked as initialized, so removing the var re-enables init
        self.assertFalse(rel_imp._initialized)

    def test_init_without_file(self):
        # interactive console: no __file__ in globals
        env = {'__name__': '__main__'}
        exec('import rel_imp; rel_imp.init()', env)
        self.assertNotIn('__package__', env)

    def test_init_with_package_already_set(self):
        env = fake_main_env()
        env['__package__'] = 'already.solved'
        exec('import rel_imp; rel_imp.init()', env)
        self.assertEqual('already.solved', env['__package__'])

    def test_init_implicitly(self):
        env = fake_main_env()
        exec('import rel_imp; rel_imp.init_implicitly()', env)
        self.assertEqual(TESTS_PKG, env['__package__'])

    def test_import_relative_import(self):
        # force re-import so init_implicitly runs inside our fake __main__
        saved = sys.modules.pop('relative_import', None)

        def restore():
            if saved is None:
                sys.modules.pop('relative_import', None)
            else:
                sys.modules['relative_import'] = saved
        self.addCleanup(restore)
        env = fake_main_env()
        exec('import relative_import', env)
        self.assertEqual(TESTS_PKG, env['__package__'])

    def test_init_script_is_init_py(self):
        # a package's __init__.py run as __main__ is its own package
        env = fake_main_env(path.join('package_test_parent', '__init__.py'))
        # when this file runs as a script, sys.path contains the tests
        # directory itself, which would be picked as the closest search path
        tests_dir = path.join(REPO_ROOT, TESTS_PKG)
        if tests_dir in sys.path:
            sys.path.remove(tests_dir)
            self.addCleanup(sys.path.insert, 0, tests_dir)
        pkg_str = TESTS_PKG + '.package_test_parent'
        main = sys.modules['__main__']
        had_path = hasattr(main, '__path__')
        old_path = getattr(main, '__path__', None)
        old_pkg_mod = sys.modules.get(pkg_str)

        def restore():
            if had_path:
                main.__path__ = old_path
            elif hasattr(main, '__path__'):
                del main.__path__
            if old_pkg_mod is None:
                sys.modules.pop(pkg_str, None)
            else:
                sys.modules[pkg_str] = old_pkg_mod
        self.addCleanup(restore)

        exec('import rel_imp; rel_imp.init()', env)
        self.assertEqual(pkg_str, env['__package__'])

    def test_init_top_level_init_py(self):
        # a top-level package's __init__.py as __main__ has no parent package
        env = fake_main_env('__init__.py')
        tests_dir = path.join(REPO_ROOT, TESTS_PKG)
        if tests_dir in sys.path:
            sys.path.remove(tests_dir)
            self.addCleanup(sys.path.insert, 0, tests_dir)
        main = sys.modules['__main__']
        had_path = hasattr(main, '__path__')
        old_path = getattr(main, '__path__', None)
        old_pkg_mod = sys.modules.get(TESTS_PKG)

        def restore():
            if had_path:
                main.__path__ = old_path
            elif hasattr(main, '__path__'):
                del main.__path__
            if old_pkg_mod is None:
                sys.modules.pop(TESTS_PKG, None)
            else:
                sys.modules[TESTS_PKG] = old_pkg_mod
        self.addCleanup(restore)

        exec('import rel_imp; rel_imp.init()', env)
        self.assertEqual(TESTS_PKG, env['__package__'])

    def test_init_unimportable_package(self):
        # __file__ inside a directory that isn't an importable package:
        # the ImportError must be caught and only logged
        env = fake_main_env(path.join('..', 'no_such_pkg_xyz', 'f.py'))
        buf = StringIO()
        with redirect_stderr(buf):
            exec('import rel_imp; rel_imp.init()', env)
        self.assertNotIn('__package__', env)
        self.assertIn('Ignoring it', buf.getvalue())

    def test_init_tolerates_unexpected_errors(self):
        env = fake_main_env()
        buf = StringIO()
        with mock.patch('rel_imp._solve_pkg', side_effect=RuntimeError('boom')), \
                redirect_stderr(buf):
            exec('import rel_imp; rel_imp.init()', env)
        self.assertNotIn('__package__', env)
        self.assertIn('Ignoring it', buf.getvalue())


class TestSolvePkg(RelImpTestCase):

    def test_solve_pkg_no_search_path(self):
        main_globals = {'__file__': '/nonexistent_dir_xyz_123/f.py'}
        self.assertIsNone(_solve_pkg(main_globals))
        self.assertNotIn('__package__', main_globals)

    def test_try_search_paths_with_pwd(self):
        # relative __file__ + PWD env var resolves through the PWD strategy
        old_pwd = os.environ.get('PWD')
        os.environ['PWD'] = path.join(REPO_ROOT, TESTS_PKG)
        if old_pwd is None:
            self.addCleanup(os.environ.pop, 'PWD')
        else:
            self.addCleanup(os.environ.__setitem__, 'PWD', old_pwd)
        main_dir, search_path = _try_search_paths({'__file__': 'fake_main.py'})
        self.assertEqual(path.join(REPO_ROOT, TESTS_PKG), main_dir)
        self.assertEqual(REPO_ROOT, search_path)


if __name__ == '__main__':
    unittest.main()
