'''
Import this module to enable relative importing on a submodule/subpackage 
running it as a main module. 
This is useful for running smoke tests or small scripts within the module.

This utility is not intended to be run on production code, rather to reduce
developing cycles times.
'''

from inspect import currentframe
from os import path
import importlib
import sys

def __solve_import_paths():
    try:
        from smoothtest_settings import Settings
        settings = Settings()
        if not (settings and settings.relative_import_enabled):
            if not settings.relative_import_enabled:
                print >> sys.stderr, 'Relative import not enabled in settings.'
            return
        return settings.relative_import_paths or list(sys.path)
    
    except ImportError:
        pass

def __get_python_path(caller_dir, import_paths):
    paths = []
    #look for paths containing the file
    for imp_pth in import_paths:
        imp_pth = path.abspath(imp_pth) 
        if (imp_pth != caller_dir
            and imp_pth == path.commonprefix((imp_pth, caller_dir))):
            paths.append(imp_pth)
    #look for the largest common python path
    if paths:
        paths.sort()
        return paths[-1]

def __get_package_str(caller_dir, python_path):
    rel = path.relpath(caller_dir, python_path)
    return rel.replace(path.sep, '.')

def __enable_relative_import(frames_back=2):
    #solve caller locals
    frame = currentframe()
    for _ in range(frames_back):
        frame = frame.f_back
    caller_locals = frame.f_locals
    #solve settings
    import_paths = __solve_import_paths()
    #solve the relative path to one of the python paths provided
    caller_dir = caller_locals['__file__']
    caller_dir = path.dirname(path.abspath(caller_dir))
    python_path = __get_python_path(caller_dir, import_paths)
    if not python_path:
        return
    #solve package and import
    pkg_str = __get_package_str(caller_dir, python_path)
    try:
        importlib.import_module(pkg_str)
        #finally enable relative import
        caller_locals['__package__'] = pkg_str
    except ImportError as e:
        print >> sys.stderr, e 

__enable_relative_import()
