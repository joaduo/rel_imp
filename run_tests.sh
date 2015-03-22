#!/bin/bash

# Unittest arguments
py_args="-m unittest discover "
# This discover is different since it moves the start path (and previously create a now-fixed bug)
discover="-m unittest discover -s rel_imp_tests/unittest_discover/"

# Print help if --help was passed
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

#set verbose flag
verbose=""
if [[ "$*" == *-v* ]] ; then
  verbose="True"
fi

#Set python commands (python 2, 3 or wine)
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


# Function to log executed commands and return their return value
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
  # Error flag, if 1, there was an error
  let error_flag=0
  # We don't run these tests on wine (not sure why)
  if [[ "$*" != *--wine* ]] ; then
    # Run each test script __main__ (because of the nature of rel_imp)
    # unittest is invoked inside each test script
    for t in $(find rel_imp_tests/ -iname "*.py" -exec grep "unittest" {} -l \;) ; do
        while read -r pcmd ; do
            # Run test for each python version
            if ! exec_test "$pcmd $t" ; then
              # test return value was not 0
              let error_flag=1
            fi
        done < <(echo "$pycmds")
    done
  fi

  # Now we use unittest discover to check any other errors, but rel_imp functionality is eclipsed
  # since scripts are not run as __main__
  while read -r pcmd ; do
    # Run test for each python version
    while read -r arg ; do
        # Run test for each unittest invocation
        if ! exec_test "$pcmd $arg" ; then
          let error_flag=1
        fi
    done < <(echo "$py_args
$discover")
  done < <(echo "$pycmds")
  
  return $error_flag
}


# Main entry point
if run_tests $* ; then
    # If everything went OK, we need to print something
    echo 
    echo "-----------> All tests passed OK"
    exit 0
else
    # If something went wrong it will display the erroring command
    exit 1
fi
