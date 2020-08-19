'''
Copyright (c) 2014 Joaquin Duo - File under MIT License

Import this module to enable explicit relative importing on a submodule or
sub-package running it as a main module. Doing so is useful for running smoke
tests or small scripts within the module.

Usage:
------

To enable explicit relative importing in __main__, you simply import
this package before any relative import

    import rel_imp; rel_imp.init()
    from .my_pkg import foo, bar
    ...

Make sure your PYTHONPATH is correctly set to solve the relative path of the
submodule/subpackage.
'''
from inspect import currentframe
from os import path
import importlib
import sys
import os
import traceback


__all__ = ['init']


def _get_search_path(main_file_dir, sys_path):
    '''
    Find the parent python path that contains the __main__'s file directory

    :param main_file_dir: __main__'s file directory
    :param sys_path: paths list to match directory against (like sys.path)
    '''
    # List to gather candidate parent paths
    paths = []
    # look for paths containing the directory
    for pth in sys_path:
        # convert relative path to absolute
        pth = path.abspath(pth)
        # filter out __main__'s file directory, it will be in the sys.path
        # filter in parent paths containing the package
        if (pth != main_file_dir
                and pth == path.commonprefix((pth, main_file_dir))):
            paths.append(pth)
    # check if we have results
    if paths:
        # we found candidates, look for the largest(closest) parent search path
        paths.sort()
        return paths[-1]


def _print_exc(e):
    '''
    Log exception as error.
    :param e: exception to be logged.
    '''
    msg = ('Exception enabling relative_import for __main__. Ignoring it: %r'
           '\n  relative_import won\'t be enabled.')
    _log_error(msg % e)


def _try_search_paths(main_globals):
    '''
    Try different strategies to found the path containing the __main__'s file.
    Will try strategies, in the following order:
        1. Building file's path with PWD env var.
        2. Building file's path from absolute file's path.
        3. Buidling file's path from real file's path.

    :param main_globals: globals dictionary in __main__
    '''
    # try with abspath
    fl = main_globals['__file__']
    search_path = None
    if not path.isabs(fl) and os.getenv('PWD'):
        # Build absolute path from PWD if possible
        cwd_fl = path.abspath(path.join(os.getenv('PWD'), fl))
        main_dir = path.dirname(cwd_fl)
        search_path = _get_search_path(main_dir, sys.path)

    if not search_path:
        # try absolute strategy (will fail on some symlinks configs)
        main_dir = path.dirname(path.abspath(fl))
        search_path = _get_search_path(main_dir, sys.path)

    if not search_path:
        # try real path strategy
        main_dir = path.dirname(path.realpath(fl))
        sys_path = [path.realpath(p) for p in sys.path]
        search_path = _get_search_path(main_dir, sys_path)

    return main_dir, search_path


def _solve_pkg(main_globals):
    '''
    Find parent python path of __main__. From there solve the package
    containing __main__, import it and set __package__ variable.

    :param main_globals: globals dictionary in __main__
    '''
    # find __main__'s file directory and search path
    main_dir, search_path = _try_search_paths(main_globals)
    if not search_path:
        _log_debug('Could not solve parent python path for %r' % main_dir)
        # no candidates for search path, return
        return
    # solve package name from search path
    pkg_str = path.relpath(main_dir, search_path).replace(path.sep, '.')
    # Remove wrong starting string for site-packages
    site_pkgs = 'site-packages.'
    if pkg_str.startswith(site_pkgs):
        pkg_str = pkg_str[len(site_pkgs):]
    assert pkg_str
    _log_debug('pkg_str=%r' % pkg_str)
    # import the package in order to set __package__ value later
    try:
        if '__init__.py' in main_globals['__file__']:
            _log_debug('__init__ script. This module is its own package')
            # The __main__ is __init__.py => its own package
            # If we treat it as a normal module it would be imported twice
            # So we simply reuse it
            sys.modules[pkg_str] = sys.modules['__main__']
            # We need to set __path__ because its needed for
            # relative importing
            sys.modules[pkg_str].__path__ = [main_dir]
            # We need to import parent package, something that would
            # happen automatically in non-faked import
            parent_pkg_str = '.'.join(pkg_str.split('.')[:-1])
            if parent_pkg_str:
                importlib.import_module(parent_pkg_str)
        else:
            _log_debug('Importing package %r' % pkg_str)
            # we need to import the package to be available
            importlib.import_module(pkg_str)
        # finally enable relative import
        main_globals['__package__'] = pkg_str
        return pkg_str
    except ImportError as e:
        # In many situations we won't care if it fails, simply report error
        # main will fail anyway if finds an explicit relative import
        _print_exc(e)


def _log(msg):
    '''
    Central log function (all levels)
    :param msg: message to log
    '''
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()


def _log_debug(msg):
    '''
    Log at debug level
    :param msg: message to log
    '''
    if _log_level <= DEBUG:
        if _log_level == TRACE:
            traceback.print_stack()
        _log(msg)


def _log_error(msg):
    '''
    Log at error level
    :param msg: message to log
    '''
    if _log_level <= ERROR:
        _log(msg)


# Logging constants
ERROR = 40
DEBUG = 10
TRACE = 5
# Set default level
_log_level = ERROR

# Keeps track of rel_imp initialization
_initialized = False


def init(log_level=ERROR):
    '''
    Enables explicit relative import in sub-modules when ran as __main__
    :param log_level: module's inner logger level (equivalent to logging pkg)

    Use PYTHON_DISABLE_REL_IMP environment variable to disable the initialization
    '''
    global _initialized
    if _initialized:
        _log_debug('Initialized. Doing nothing')
        return
    elif 'PYTHON_DISABLE_REL_IMP' in os.environ:
        _log_debug('PYTHON_DISABLE_REL_IMP environment variable present. Doing nothing')
        return
    else:
        _initialized = True
    # find caller's frame
    frame = currentframe()
    # go 1 frame back to find who imported us
    frame = frame.f_back
    _init(frame, log_level)


def init_implicitly(log_level=ERROR):
    '''
    Use PYTHON_DISABLE_REL_IMP environment variable to disable the initialization
    '''
    global _initialized
    if _initialized:
        _log_debug('Initialized. Doing nothing')
        return
    elif 'PYTHON_DISABLE_REL_IMP' in os.environ:
        _log_debug('PYTHON_DISABLE_REL_IMP environment variable present. Doing nothing')
        return
    else:
        _initialized = True
    # find caller's frame
    frame = currentframe()
    while frame.f_globals['__name__'] != '__main__':
        frame = frame.f_back
    _init(frame, log_level)


def _init(frame, log_level=ERROR):
    '''
    Enables explicit relative import in sub-modules when ran as __main__
    :param log_level: module's inner logger level (equivalent to logging pkg)
    '''
    global _log_level
    _log_level = log_level
    # now we have access to the module globals
    main_globals = frame.f_globals

    # If __package__ set or it isn't the __main__, stop and return.
    # (in some cases relative_import could be called once from outside
    # __main__ if it was not called in __main__)
    # (also a reload of relative_import could trigger this function)
    pkg = main_globals.get('__package__')
    file_ = main_globals.get('__file__')
    if pkg or not file_:
        _log_debug('Package solved or init was called from interactive '
                   'console. __package__=%r, __file__=%r' % (pkg, file_))
        return
    try:
        _solve_pkg(main_globals)
    except Exception as e:
        _print_exc(e)
