#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ':: Installing repo info'
wget http://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm
rpm -ivh ajenti-repo-1.0-1.noarch.rpm
rm ajenti-repo-1.0-1.noarch.rpm

echo ':: Installing package'
yum install ajenti -y

echo ':: Done! Open https://<address>:8000 in browser'
