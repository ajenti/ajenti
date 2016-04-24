#!/bin/bash
rm ~/.ssh/id_rsa
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
echo -en 'travis_fold:start:deps.apt\r'
    echo Installing packages
    #sudo apt-get install -y python-lxml python-dbus python-lxml python-augeas
echo -en 'travis_fold:end:deps.apt\r'
