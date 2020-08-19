# -*- coding: utf-8 -*-
'''
Copyright (c) 2015 Joaquin Duo - File under MIT License

Code Licensed under MIT License. See LICENSE file.

To enable explicit relative importing in __main__, you simply import
this package before any relative import

Usage:
------

To enable explicit relative importing in __main__, you simply import
this package before any relative import

    import relative_import
    from .my_pkg import foo, bar
    ...

There is no need to call any init function using this module.
Make sure your PYTHONPATH is correctly set to solve the relative path of the
submodule/subpackage.
'''

import rel_imp

rel_imp.init_implicitly()
