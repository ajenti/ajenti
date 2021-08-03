#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ':: Adding EPEL repo'
rpm -ivh https://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm 

echo ':: Adding Ajenti repo'
rpm -ivh https://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm

echo ':: Installing package'
yum install ajenti -y

echo ':: Done! Open https://<address>:8000 in browser'
