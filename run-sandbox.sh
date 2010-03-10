#!/bin/bash

echo Cleaning
rm sandbox/* -rf

echo Building the sandbox
mkdir sandbox/ajenti
echo '* Copying Ajenti'
cp ajenti/* sandbox/ajenti/ -r

echo '* Copying Ajenti plugins'
mkdir sandbox/ajenti/plugins
ls plugins/ | xargs -i sh -c 'cp plugins/{}/* sandbox/ajenti/plugins/ -r'

DIR=`pwd`

echo
echo Starting Ajenti
cd sandbox/ajenti && python main.py

echo Sandbox run finished
cd $DIR

echo Cleaning
rm sandbox/* -rf
