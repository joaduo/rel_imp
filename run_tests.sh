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

let errors=0
#Log executed commands
function exec_cmd(){
  local out=$(eval "$*" 2>&1 )
  local ok=$(echo "$out" | tail -n 1)
  if  echo "$ok" | grep OK > /dev/null ; then
    return 0
  else
    let errors=1
    echo "--------------------"
    echo "$*"
    echo "$ok"
    echo
#     echo "$out"
    return 1
  fi
}

if [ "$1" != "wine" ] ; then
  #We need to run each test as __main__, if not, we lose the testing
  for t in $(grep "unittest" rel_imp_tests/*.py -l) ; do
      exec_cmd "python $t"
      exec_cmd "python3 $t"
  done
fi

echo "$pycmds" | while read pcmd
do
    exec_cmd "$pcmd $args"
done

# echo errors $errors

if [ "$errors" == "1" ] ; then
    exit 1
else
    echo 
    echo "-----------> All tests passed OK"
    echo
    exit 0
fi
