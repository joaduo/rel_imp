#!/bin/bash
 
bash ./run_tests.sh
ret=$?
if [[ "$ret" == "0" ]] ; then

    if ! pandoc --from=markdown --to=rst --output=README README.md ; then
        echo "pandoc command failed. Probably it is not installed. Aborting."
        exit 1
    fi
    #Clean output urls
    sed 's/\\\_/_/g' -i README

    app="rel_imp"

    rm dist/$app\-*.tar.gz

    python setup.py sdist && python setup.py check -r

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
    fi

    pkg=`ls dist/$app\-*.tar.gz`
    echo
    echo "upload with: twine upload $pkg"

fi

