'''
Copyright (c) 2014 Joaquin Duo - File under MIT License

Import this module to enable explicit relative importing on a submodule or
sub-package running it as a main module. Doing so is useful for running smoke 
tests or small scripts within the module.

If you are using this tool enabled on production, make sure you do enough 
testing. (since it does some guessing trying to find the right package of
the module)

Usage:
------

To enable explicit relative importing in __main__, you simply import
this package before any relative import

import relative_import

from .my_pkg import foo, bar

Make sure your PYTHON_PATH is correctly set to solve the relative path of the
submodule/subpackage.

'''
from __future__ import print_function
from inspect import currentframe
from os import path
import importlib
import sys


def __get_search_path(main_file_dir, sys_path):
    #Gather candidate search paths
    paths = []
    #look for paths containing the file
    for pth in sys_path:
        #convert relative path to absolute
        pth = path.abspath(pth)
        #filter __main__'s file directory, naturally it will be in the sys.path
        #filter parent paths containing the package
        if (pth != main_file_dir
            and pth == path.commonprefix((pth, main_file_dir))):
            paths.append(pth)
    #check if we have results
    if paths:
        #we found candidates
        #now look for the largest parent search path
        paths.sort()
        return paths[-1]

def __print_exc(e):
    msg = ('Exception enabling relative_import for __main__. Ignoring it: %r'
           '\n  relative_import won\'t be enabled.')
    print(msg % e, file=sys.stderr)

def __solve_pkg(main_globals):
    #find __main__'s file directory
    main_file_dir = path.dirname(path.abspath(main_globals['__file__']))
    search_path = __get_search_path(main_file_dir, sys.path)
    #no candidates for search path
    if not search_path:
        return
    #solve package name from search path
    pkg_str = path.relpath(main_file_dir, search_path).replace(path.sep, '.')
    #import the package in order to set __package__ value later
    try:
        if '__init__.py' in main_globals['__file__']:
            #The __main__ is __init__.py => its own package
            #If we treat it as a normal module it would be imported twice
            #So we simply reuse it
            sys.modules[pkg_str] = sys.modules['__main__']
            #We need to set __path__ because its needed for
            #relative importing
            sys.modules[pkg_str].__path__ = [main_file_dir]
        else:
            #we need to import the package to be available
            importlib.import_module(pkg_str)
        #finally enable relative import
        main_globals['__package__'] = pkg_str
        return pkg_str
    except ImportError as e:
        #In many situations we won't care if it fails, simply report error
        #main will fail anyway if finds an explicit relative import
        __print_exc(e)

def init():
    '''
    Enables explicit relative import in sub-modules when ran as __main__
    '''
    #find caller locals
    frame = currentframe()
    #go two frames back to find who imported us
    for _ in range(1):
        frame = frame.f_back
    #now we have access to the module globals
    main_globals = frame.f_globals

    #If __package__ is already set or its not the __main__, stop doing anything.
    # (in some cases relative_import could be called once from outside
    # __main__ if it was not called in __main__)
    # (also a reload of relative_import could trigger this function)
    if main_globals.get('__package__') or main_globals.get('__name__') != '__main__':
        return
    
    try:
        __solve_pkg(main_globals)
    except Exception as e:
        __print_exc(e)

