#!/bin/bash
 
bash ./run_tests.sh
ret=$?
if [[ $ret == "0" ]] ; then

    app="rel_imp"

    rm -f dist/$app\-*.tar.gz

    if ! python3 -m build ; then
        echo "build failed. You may need to: pip install build"
        exit 1
    fi

    if [ "$1" == "venv" ] ;  then
            #test installation
            mkdir venv -p
            cd venv
            virtualenv ./
            source bin/activate
            pip install ../dist/$app\-*.tar.gz
            pip uninstall $app -y
            cd ..
            #rm venv -Rf

            mkdir venv3 -p
            cd venv3
            virtualenv ./ -p python3
            source bin/activate
            pip install ../dist/$app\-*.tar.gz
            pip uninstall $app -y
            cd ..
            rm venv3 -Rf
    fi

    pkg=`ls dist/$app\-*.tar.gz`
    echo
    echo "upload with: twine upload $pkg"

fi
