#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ':: Installing repo key'
wget http://repo.ajenti.org/debian/key -O- | apt-key add -

echo ':: Adding repo entry'
echo "deb http://repo.ajenti.org/debian main main debian" >> /etc/apt/sources.list.d/ajenti.list

echo ':: Updating lists'
apt-get update

echo ':: Installing packages'
apt-get install -y ajenti 
apt-get install -y python-pip python-dev libevent-dev 
pip install -U gevent 
pip install greenlet==dev 
pip install psutil --upgrade 
/etc/init.d/ajenti restart 

echo ':: Done! Open https://<address>:8000 in browser'
