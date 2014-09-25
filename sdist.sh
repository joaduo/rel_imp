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
pip install ../dist/relative_import-0.1.1.tar.gz
pip uninstall relative_import -y
cd ..
#rm venv -Rf

#Leave message
echo 
echo "upload with: python setup.py sdist upload -r pypi"
