#!/bin/bash
echo -en 'travis_fold:start:Python modules\r'
    sudo apt-get install -y python-lxml python-dbus python-lxml
    pip install -r ajenti-core/requirements.txt
    pip install -r plugins/core/requirements.txt
    pip install -r plugins/services/requirements.txt
    pip install -r plugins/terminal/requirements.txt
    pip install ajenti-dev-multitool
echo -en 'travis_fold:end:Python modules\r'

echo -en 'travis_fold:start:Node modules\r'
    npm install -g bower
    cd tests-karma
    npm install || exit 1
    cd ..
echo -en 'travis_fold:end:Node modules\r'

echo -en 'travis_fold:start:Bower components\r'
    ajenti-dev-multitool --bower install || exit 1
echo -en 'travis_fold:end:Bower components\r'

echo -en 'travis_fold:start:Nose unit tests\r'
    cd tests-nose
    nosetests base.py || exit 1
    cd ..
echo -en 'travis_fold:end:Nose unit tests\r'

echo -en 'travis_fold:start:Karma unit tests\r'
    cd tests-karma
    ./node_modules/.bin/karma start karma.conf.coffee --single-run || exit 1
    cat coverage/coverage.txt
    cd ..
echo -en 'travis_fold:end:Karma unit tests\r'
