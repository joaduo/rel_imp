import sys
from setuptools import setup

name = 'rel_imp'


def in_python3():
    return sys.version_info[0] > 2

def long_description():
    with open('README', 'r') as f:
        if in_python3():
            return f.read()
        else:
            return unicode(f.read())


setup(
    name=name,
    py_modules=[name],
    version='0.2.8',
    description='Enable explicit relative imports in __main__ module.',
    long_description=long_description(),
    author='Joaquin Duo',
    author_email='joaduo@gmail.com',
    license='MIT',
    url='https://github.com/joaduo/' + name,
    keywords=['explicit', 'relative', 'import'],
    install_requires=([] if in_python3() else ['importlib']),
)
