The relative_import utility
===========================

Relative import tool for running subpackages or submodules as main scripts (enabling relative imports)

Installation
------------
Clone the repo into one of your PYTHON_PATHs

```
clone https://github.com/joaduo/relative_import.git
```

How to use it?
--------------

Imagine you have 2 modules inside a package called "my_pkg".

That would be:

* `my_pkg/__init__.py`
* `my_pkg/math_lib.py`
* `my_pkg/test.py`

So in test.py we could have

```python
from .math_lib import factorize

def print_factorize(number):
    num = factorize(number)
    print num

if __name__ == '__main__':
    #Small smoke test
    factorize_and_print(10)
    factorize_and_print(0)
    factorize_and_print(-10)
```
If you do `python my_pkg/test.py` it will throw an exception because of the relative import at the first line.

PEP 366 presents a workaround like:
```python
if __name__ == "__main__" and __package__ is None:
    __package__ = "my_pkg"

from .math_lib import factorize

```

This will make the code work, but it is not an elegant solution. 

So you can use `relative_import` to make your code look nicer like. Simply do:
```python
import relative_import
from .math_lib import factorize

```
It is equivalent as the PEP's solution but you don't have to worry about keeping in sync `__package__`'s value

How does it work?
-----------------

It uses the same technique in PEP 366 but `__package__`'s value is set through dynamic inspection of the stack. To solve the value of `__package__` it compares the current `__main__`'s file with paths in sys.path - or, optionally, a list of paths given in the preferences-.

For example, for a file in `/home/user/projects/python/math/my_pkg/test.py` given the following paths in sys.path:
```python
[
'/home/user/projects/python/',
'/home/user/projects/python/math/',
'/home/user/projects/python/math/my_pkg/',
]
```
It will pick the closest path to the `__main__`'s file that is not the `__main__`'s file's directory.

Then the base path use to solve `__package__` variable will be `/home/user/projects/python/math/`

Preferences
-----------

This package works out-of-the-box without any configuration, but you can set certain preferences.

To do so, create a `relative_import_settings.py` in one of your PYTHON_PATHs. Should be like

```python

class Settings(object):
    #Self explanatory, if False relate_import won't work
    relative_import_enabled = True
    #instead of searching in sys.path, use this list
    #beware, if empty, it will look into sys.path anyway
    relative_import_path = ['/some/path/to/project/']

```

TODO
----

Create pypi install package.


Related PEPs
------------

* http://legacy.python.org/dev/peps/pep-0328/
* http://legacy.python.org/dev/peps/pep-0366/
