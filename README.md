# The relative_import utility

Enabling relative imports in main modules the easy way.

For enabling relative import in `__main__` module PEP 366 presents a workaround like:
```python
if __name__ == "__main__" and __package__ is None:
    __package__ = "my_pkg"

from .foo import bar
```

With `relative_import` you can rewrite it as:
```python
import relative_import
from .foo import bar
```

Cleaner, faster and less coupled. (you don't need to specify the package manually)

**Note:** In order to use `relative_import` the module must be inside a package or sub-package. 

## Why using explicit relative imports? 

Python 2 still supports implicit relative import and will be deprecated in 3, so you will want to migrate those scripts using implicit relative import to explicit relative import. Check more on the [PEP 404](http://legacy.python.org/dev/peps/pep-0404/#id18).

Explicit relative imports makes your code less coupled. As [PEP 328](http://legacy.python.org/dev/peps/pep-0328/#rationale-for-relative-imports) says:

> Several use cases were presented, the most important of which is being able to rearrange the structure of large packages without having to edit sub-packages. In addition, a module inside a package can't easily import itself without relative imports. 

Although it is still a matter of taste. (I personally prefer less code to express the same)

## Why running sub-modules as main?

Some reasons:

1. A submodule can become a command line tool if called as main.
2. You can have unit test or smoke test within the module.
3. You simply want to run it without any explicit test to see if at least it imports everything it needs.  

## Installation

1. Clone the repo into one of your module search path (paths are generally set through the PYTHONPATH environment variable).

```
clone https://github.com/joaduo/relative_import.git
```

2. Download the `__init__.py` and save as `relative_import.py` in one of your module search path.

```
wget https://raw.githubusercontent.com/joaduo/relative_import/master/__init__.py -O relative_import.py
```

## Example

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

So you can use `relative_import` to make your code look nicer. Simply do:
```python
import relative_import
from .math_lib import factorize
```
It is equivalent as the prior solution but you don't have to worry about keeping in sync `__package__`'s value.

## How does it work?

It uses the same technique in PEP 366 but `__package__`'s value is set through dynamic inspection of the stack. To solve the value of `__package__` it compares the current `__main__`'s file with search paths in sys.path - or, optionally, a list of paths given in the settings -.

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

## Disabling relative_import

Relative import shouldn't have any non-desired side effect, but if for some reason you want to disable you can:

1. Comment the `__enable_relative_import()` line in the `__init__.py` or `relative_import.py` file
2. Create an empty `relative_import.py` in a PYTHONPATH with higher priority than the installed one

Remember that relative_import code runs only on the first time its imported, so you won't gain any performance or difference disabling it.

## TODO

Create pypi install package.

## Feedback or bugs reporting

File an issue through github's [issue tracking system](https://github.com/joaduo/relative_import/issues).

You can optionally contact me at joaduo gmail com.

## Related PEPs

* http://legacy.python.org/dev/peps/pep-0328/
* http://legacy.python.org/dev/peps/pep-0366/
