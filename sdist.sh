#!/bin/bash
 
source run_tests.sh

#Convert markdown to rst
pandoc --from=markdown --to=rst --output=README README.md

#build package
python setup.py sdist && python setup.py check -r

#test installation
mkdir venv -p
cd venv
virtualenv ./
source bin/activate
pip install ../dist/rel_imp-*.tar.gz
pip uninstall rel_imp -y
cd ..
#rm venv -Rf

#Leave message
echo 
echo "upload with: python setup.py sdist upload -r pypi"
