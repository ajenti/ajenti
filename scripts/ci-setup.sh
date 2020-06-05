#!/bin/bash
echo -en 'travis_fold:start:deps.apt\r'
    echo Installing packages
    sudo python3 -m pip install wheel setuptools
    #sudo apt-get install -y python-lxml python-dbus python-lxml python-augeas
echo -en 'travis_fold:end:deps.apt\r'
