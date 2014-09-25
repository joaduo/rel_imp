#!/bin/bash

args="-m unittest discover"

#Checking in current platform
python $args

python3 $args

#We need to run each test as __main__, if not, we lose the testing
for t in $(ls rel_imp_tests/*.py) ; do
	python $t
	python3 $t
done 

#test in wine
wine python $args
wine c:\\Python33\\python.exe $args
