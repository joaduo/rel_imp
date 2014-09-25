#!/bin/bash

#Checking in current platform
python -m unittest discover

python3 -m unittest discover

#We need to run each test as __main__, if not, we lose the testing
for t in $(ls rel_imp_tests/*.py) ; do
	python $t
	python3 $t
done 

#test in wine
wine python -m unittest discover
