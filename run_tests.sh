#!/bin/bash

py_args="-m unittest discover "
#this discover is different since it moves the start path (and gave a bug in the pass)
discover="-m unittest discover -s rel_imp_tests/unittest_discover/"

if [[ "$*" == *--help* ]] ; then
  #Test commands in for wine
  help="
$0 [options]

options

  --help        this help
  -v            verbose
  --wine        run wine tests
  --py2         run python 2 tests
  --py3         run python 3 tests exclusively

  "
  echo "$help"
  exit 0
fi


verbose=""
if [[ "$*" == *-v* ]] ; then
  verbose="True"
fi


if [[ "$*" == *--wine* ]] ; then
  #Test commands in for wine
  pycmds="wine python
wine c:\\\\\\\\Python33\\\\\\\\python.exe"
elif [[ "$*" == *--py2* ]] ; then
  #Test commands on current platform
  pycmds="python"
elif [[ "$*" == *--py3* ]] ; then
  #Test commands on current platform
  pycmds="python3"
else
  #Test commands on current platform
  pycmds="python
python3"
fi


#Log executed commands
function exec_test(){
  local out=$(eval "$*" 2>&1 )
  if [ -n "$verbose" ] ; then
    echo "$*"
    echo "$out"
  fi
  local ok=$(echo "$out" | tail -n 1)
  if  echo "$ok" | grep OK > /dev/null ; then
    return 0
  else
    echo "--------------------"
    echo "$*"
    echo "$ok"
    echo
    return 1
  fi
}


function run_tests(){
  let test_errored=0
  if [[ "$*" != *--wine* ]] ; then
    #We need to run each test as __main__, if not, we lose the point in testing
    for t in $(find rel_imp_tests/ -iname "*.py" -exec grep "unittest" {} -l \;) ; do
        while read -r pcmd ; do
            if ! exec_test "$pcmd $t" ; then
              let test_errored=1
            fi
        done < <(echo "$pycmds")
    done
  fi

  #Now we use unittest discover to check any errors (but not "real" test is done)
  while read -r pcmd ; do
    while read -r arg ; do
        if ! exec_test "$pcmd $arg" ; then
          let test_errored=1
        fi
    done < <(echo "$py_args
$discover")
  done < <(echo "$pycmds")
  
  return $test_errored
}


if run_tests $* ; then
    echo 
    echo "-----------> All tests passed OK"
    exit 0
else
    exit 1
fi
