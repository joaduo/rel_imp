# The rel_imp utility

[ ![Codeship Status for joaduo/rel_imp](https://codeship.com/projects/6634b790-b2f6-0132-44e8-3a4b0bbda320/status?branch=master)](https://codeship.com/projects/70108)

Enabling explicit relative imports in main modules the easy way.

For enabling relative import in `__main__` module PEP 366 presents a workaround like:
```python
if __name__ == "__main__" and __package__ is None:
    __package__ = "my_pkg"

from .foo import bar
```

With `rel_imp` you can rewrite it as:
```python
import rel_imp; rel_imp.init()
from .foo import bar
```

Cleaner, faster and less coupled. (you don't need to specify the package manually)

**Note:** In order to use `rel_imp` the module you are coding must be inside a package or a sub-package. 

## Why using explicit relative imports? 

Python 2 still supports implicit relative import and will be deprecated in Python 3, so you will want to migrate those scripts using implicit relative import to explicit relative import. Check more on the [PEP 404](http://legacy.python.org/dev/peps/pep-0404/#id18).

Explicit relative imports makes your code less coupled. As [PEP 328](http://legacy.python.org/dev/peps/pep-0328/#rationale-for-relative-imports) says:

> Several use cases were presented, the most important of which is being able to rearrange the structure of large packages without having to edit sub-packages. In addition, a module inside a package can't easily import itself without relative imports. 

Although it is still a matter of taste. (I personally prefer less code to express the same)

## Why running sub-modules as main?

Some reasons:

1. A submodule can become a command line tool if called as main.
2. You can have unit test or smoke test within the module.
3. You simply want to run it without any explicit test to see if at least it imports everything it needs.  

## Installation and Uninstallation

### Install via pip
```
pip install rel_imp
```
Remove it with:
```
pip uninstall rel_imp
```

### Install downloading the file
Download the `rel_imp.py` in one your Python's search path.

```
wget https://raw.githubusercontent.com/joaduo/rel_imp/master/rel_imp.py
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

def factorize_and_print(number):
    num = factorize(number)
    print num

if __name__ == '__main__':
    #Small smoke test
    factorize_and_print(10)
    factorize_and_print(0)
    factorize_and_print(-10)
```

If you do `python my_pkg/test.py` it will throw an exception because of the relative import at the first line.

So you can use `rel_imp` to make your code look nicer. Simply do:
```python
import rel_imp; rel_imp.init()
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

## Disabling rel_imp

Relative import shouldn't have any non-desired side effect, but if for some reason you want to disable it:

1. Replace the `def init()` function in the `rel_imp.py` file (if you downloaded it)
2. Create an empty `rel_imp.py` with a dummy `init()` in a PYTHONPATH with higher priority than the installed one (or optionally uninstall the original one)

`rel_imp` is really lightweight so you won't gain any performance difference disabling it.

## Feedback or bugs reporting

File an issue through github's [issue tracking system](https://github.com/joaduo/rel_imp/issues).

You can optionally contact me at joaduo gmail com.

## Related PEPs

* http://legacy.python.org/dev/peps/pep-0328/
* http://legacy.python.org/dev/peps/pep-0366/
