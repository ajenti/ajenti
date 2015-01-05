#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo ':: Adding EPEL repo'
rpm -ivh http://download.fedoraproject.org/pub/epel/beta/7/x86_64/epel-release-7-1.noarch.rpm || true

echo ':: Switching from MariaDB (default) to MySQL (new)'
rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm 

echo ':: Adding Ajenti repo'
rpm -ivh http://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm

echo ':: Installing package'
yum install ajenti -y

echo ':: Done! Open https://<address>:8000 in browser'
