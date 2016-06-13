#!/bin/bash
 
bash ./run_tests.sh
ret=$?
if [[ "$ret" == "0" ]] ; then

	#Convert markdown to rst
	if ! pandoc --from=markdown --to=rst --output=README README.md ; then
		echo "pandoc command failed. Probably it is not installed. Aborting."
		exit 1
	fi
	
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

fi