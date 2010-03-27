#!/bin/bash

mkdir sandbox 2> /dev/null

echo Cleaning
rm sandbox/* -rf
 
echo Building the sandbox
echo '* Copying Ajenti'
mkdir sandbox/ajenti
cp ajenti/* sandbox/ajenti/ -r

echo '* Copying Ajenti Backup'
mkdir sandbox/ajenti-backup
cp ajenti-backup/* sandbox/ajenti-backup/ -r

echo '* Copying Ajenti plugins'
mkdir sandbox/ajenti/plugins
ls plugins/ | xargs -i sh -c 'cp plugins/{}/* sandbox/ajenti/plugins/ -r'

DIR=`pwd`

echo
echo Starting Ajenti
cd sandbox/ajenti && python main.py

cd $DIR
