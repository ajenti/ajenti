#! /bin/bash

echo "Install Python requirements"
/usr/bin/python3 -m pip install pip --upgrade
/usr/bin/python3 -m pip install -r /etc/ajenti/requirements.txt 

echo "Generate SSL certificate"
/usr/local/bin/ajenti-ssl-gen $(hostname)

echo "Cleanup"
rm -f /etc/ajenti/requirements.txt
