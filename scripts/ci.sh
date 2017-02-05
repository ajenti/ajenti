#!/bin/bash
echo -en 'travis_fold:start:deps.python\r'
    echo Installing Python modules
    pip install -r ajenti-core/requirements.txt
    pip install -r plugins/core/requirements.txt
    pip install -r plugins/augeas/requirements.txt
    pip install -r plugins/auth_users/requirements.txt
    pip install -r plugins/datetime/requirements.txt
    pip install -r plugins/services/requirements.txt
    pip install -r plugins/terminal/requirements.txt
    pip install ajenti-dev-multitool
echo -en 'travis_fold:end:deps.python\r'

echo -en 'travis_fold:start:deps.node\r'
    echo Installing NodeJS modules
    npm install -g bower babel-cli babel-preset-es2015 babel-plugin-external-helpers less npm@3
    npm install babel-cli babel-preset-es2015 babel-plugin-external-helpers
    cd tests-karma
    npm install || exit 1
    cd ..
echo -en 'travis_fold:end:deps.node\r'

echo -en 'travis_fold:start:deps.bower\r'
    echo Installing Bower components
    ajenti-dev-multitool --bower install || exit 1
echo -en 'travis_fold:end:deps.bower\r'

echo -en 'travis_fold:start:test.nose\r'
    echo Running Nose tests
    cd tests-nose
    nosetests tests || exit 1
    cd ..
echo -en 'travis_fold:end:test.nose\r'

echo -en 'travis_fold:start:test.karma\r'
    echo Running Karma tests
    ajenti-dev-multitool --build || exit 1
    cd tests-karma
    ./node_modules/.bin/karma start karma.conf.coffee --single-run || exit 1
    cat coverage/coverage.txt
    cd ..
echo -en 'travis_fold:end:test.karma\r'
