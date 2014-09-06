'''
Copyright (c) 2014 Joaquin Duo - File under MIT License

Import this module to enable relative importing on a submodule/subpackage 
running it as a main module. 
This is useful for running smoke tests or small scripts within the module.

This utility is not intended to be run on production code, rather to reduce
developing cycles times.

Usage:
------

To enable relative importing in a submodule ran as __main__, you simply import
this package
import relative_import

Make sure your PYTHON_PATH is correctly set to solve the relative path of the 
submodule/subpackage.

'''

from inspect import currentframe
from os import path
import importlib
import sys

def __solve_import_paths():
    try:
        from relative_import_settings import Settings
        settings = Settings()
        if not (settings and settings.relative_import_enabled):
            if not settings.relative_import_enabled:
                print >> sys.stderr, 'Relative import not enabled in settings.'
            return
        return settings.relative_import_path or list(sys.path)
    
    except ImportError:
        pass

def __get_python_path(caller_dir, import_path):
    paths = []
    #look for paths containing the file
    for imp_pth in import_path:
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

def __enable_relative_import():
    #solve caller locals
    frame = currentframe()
    #go to frames back to find who imported us
    for _ in range(2):
        frame = frame.f_back
    #now we have access to the locals :)
    caller_locals = frame.f_locals
    #already set or not __main__, stop doing anything.
    #In general this function won't be called twice (since it's only called
    #the first time the package is loaded (but could be called the first
    #time from one non __main__ module
    if caller_locals['__package__'] or caller_locals['__name__'] != '__main__':
        return 
    #solve settings
    import_path = __solve_import_paths()
    #disabled or no import paths
    if not import_path:
        return
    #solve the relative path to one of the python paths provided
    caller_dir = caller_locals['__file__']
    caller_dir = path.dirname(path.abspath(caller_dir))
    python_path = __get_python_path(caller_dir, import_path)
    if not python_path:
        return
    #solve package name
    pkg_str = __get_package_str(caller_dir, python_path)
    #import it
    try:
        if '__init__.py' in caller_locals['__file__']:
            #The __main__ is its own package
            #If we treat it as a normal module it would be imported twice
            sys.modules[pkg_str] = sys.modules['__main__']
            #We need to set __path__ because its needed for
            #relative importing
            sys.modules[pkg_str].__path__ = [caller_dir]
        else:
            #we need to import 
            importlib.import_module(pkg_str)
        #finally enable relative import
        caller_locals['__package__'] = pkg_str
    except ImportError as e:
        #In many situations we won't care if it fails
        #it will fail anyway if it finds an relative import in __main__
        print >> sys.stderr, e 

__enable_relative_import()
