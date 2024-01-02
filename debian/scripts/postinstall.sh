#! /bin/bash

echo "Install Python requirements"
/usr/bin/python3 -m pip install pip --upgrade
/usr/bin/python3 -m pip install -r /etc/ajenti/requirements.txt 

echo "Checking config.yml"
if [ ! -f /etc/ajenti/config.yml ]; then
	mkdir -p /etc/ajenti
	cat << EOF > /etc/ajenti/config.yml
auth:
  allow_sudo: true
  emails: {}
  provider: os
  users_file: /etc/ajenti/users.yml
bind:
  host: 0.0.0.0
  mode: tcp
  port: 8000
color: default
max_sessions: 9
name: $(hostname)
session_max_time: 3600
ssl:
  certificate:
  client_auth:
    certificates: []
    enable: false
    force: false
  enable: false
  fqdn_certificate: null
email:
  enable: false
  smtp:
    password: ''
    port: ''
    server: ''
    user: ''
EOF
fi

if [ ! -f /etc/ajenti/users.yml ]; then
	mkdir -p /etc/ajenti
	echo "users: null" > /etc/ajenti/users.yml
fi

echo "Generate SSL certificate"
/usr/local/bin/ajenti-ssl-gen $(hostname)

echo "Cleanup"
#rm -f /etc/ajenti/requirements.txt
