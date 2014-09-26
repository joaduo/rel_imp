#!/bin/bash

args="-m unittest discover "

#Checking in current platform
#eval "python $args $filter"

if [ "$1" == "wine" ] ; then
pycmds="wine python
wine c:\\\\\\\\Python33\\\\\\\\python.exe"
else
pycmds="python
python3"
fi

#Log executed commands
function exec_cmd(){
  out=$(eval "$*" 2>&1 )
  ok=$(echo "$out" | tail -n 1)
  if [[ "$ok" == "" || "$ok" == "OK" ]]; then
    return 0
  else
    echo "--------------------"
    echo "$*"
    echo "$ok"
    echo
    #echo "$out"
    return 1
  fi
}

#We need to run each test as __main__, if not, we lose the testing
for t in $(ls rel_imp_tests/*.py) ; do
    exec_cmd "python $t"
    exec_cmd "python3 $t"
done

echo "$pycmds" | while read pcmd
do
  exec_cmd "$pcmd $args"
done
