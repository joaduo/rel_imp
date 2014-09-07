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


def __get_search_path(main_file_dir, sys_path):
    #List of candidate search paths
    paths = []
    #look for paths containing the file
    for imp_pth in sys_path:
        #convert relative path to absolute
        imp_pth = path.abspath(imp_pth)
        #filter __main__'s file directory, naturally it will be in the sys.path
        #filter parent paths containing the package
        if (imp_pth != main_file_dir
            and imp_pth == path.commonprefix((imp_pth, main_file_dir))):
            paths.append(imp_pth)
    #check if we have results
    if paths:
        #we found candidates
        #now look for the largest parent search path
        paths.sort()
        return paths[-1]


def __enable_relative_import():
    '''
    Enables explicit relative import in sub-modules when ran as __main__
    '''
    #solve caller locals
    frame = currentframe()
    #go to frames back to find who imported us
    for _ in range(2):
        frame = frame.f_back
    #now we have access to the locals
    #import ipdb; ipdb.set_trace()
    main_globals = frame.f_globals
    #already set or not __main__, stop doing anything.
    #In general this function won't be called twice (since it's only called
    #the first time the package is loaded (but could be called the first
    #time from one non __main__ module
    if main_globals['__package__'] or main_globals['__name__'] != '__main__':
        return
    #solve __main__'s file dir
    main_file_dir = path.dirname(path.abspath(main_globals['__file__']))
    search_path = __get_search_path(main_file_dir, sys.path)
    if not search_path:
        return
    #solve package name from search path
    pkg_str = path.relpath(main_file_dir, search_path).replace(path.sep, '.')
    #import the package in order to set __package__ value later
    try:
        if '__init__.py' in main_globals['__file__']:
            #The __main__ is its own package
            #If we treat it as a normal module it would be imported twice
            sys.modules[pkg_str] = sys.modules['__main__']
            #We need to set __path__ because its needed for
            #relative importing
            sys.modules[pkg_str].__path__ = [main_file_dir]
        else:
            #we need to import
            importlib.import_module(pkg_str)
        #finally enable relative import
        main_globals['__package__'] = pkg_str
    except ImportError as e:
        #In many situations we won't care if it fails
        #it will fail anyway if it finds an relative import in __main__
        print >> sys.stderr, e


__enable_relative_import()
