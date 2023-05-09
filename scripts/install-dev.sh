#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

DISTRO=
OS=
PYTHON3=$(which python3)

msg()
{
    message=$1
    echo
    # Bold and green font
    echo -e "\e[1m\e[92m$message\e[39m\e[0m"
    echo
}

if grep 'Debian' /etc/issue > /dev/null 2>&1 ; then
    OS=debian
    DISTRO=debian
fi

if grep 'Ubuntu' /etc/issue > /dev/null 2>&1 ; then
    OS=debian
    DISTRO=ubuntu
fi

if grep 'ubuntu' /etc/os-release > /dev/null 2>&1 ; then
    OS=debian
    DISTRO=ubuntu
fi


if [ ! $OS ] ; then
    echo ":: Could not detect OS"
    echo ":: Press Enter to continue"
    read -n1
fi


msg ":: OS: $OS\n:: Distro: $DISTRO"


if [ "$DISTRO" == "ubuntu" ] ; then
    msg ":: Enabling universe repository"
    add-apt-repository -y universe
fi

if [ "$OS" == "debian" ] ; then

    msg ":: Preparing nodejs package"
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -

    msg ":: Installing curl"
    apt-get update
    apt install curl

    msg ":: Preparing yarn package source list for apt"
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list

    msg ":: Installing prerequisites"
    apt-get update
    DEBIAN_FRONTEND='noninteractive' apt-get install -y build-essential python3-pip python3-venv python3-dev python3-lxml python3-dbus libffi-dev python3-augeas libssl-dev libjpeg-dev libpng-dev uuid-dev python3-apt ntpdate git yarn nodejs gettext || exit 1
fi

msg ":: Installing node dependencies"

yarn global add angular-gettext-cli @angular/cli #angular-gettext-tools

msg ":: Setting up virtual env in /opt"

$PYTHON3 -m venv /opt/ajenti --system-site-packages
source /opt/ajenti/bin/activate
PYTHON3=/opt/ajenti/bin/python3

msg ":: Upgrading PIP"

rm /usr/lib/$PYTHON3/dist-packages/setuptools.egg-info || true # for debian 7
$PYTHON3 -m pip install -U pip wheel testresources setuptools
$PYTHON3 -m pip uninstall -y gevent-socketio gevent-socketio-hartwork

msg ":: Installing Ajenti Dev Multitool"

mkdir /opt/ajenti-dev-multitool
cd /opt/ajenti-dev-multitool
git clone -b dev https://github.com/daniel-schulz/netzint-ajenti-dev-multitool.git . || exit 1
$PYTHON3 -m pip install . || exit 1

cd /opt/ajenti

msg ":: Cloning git repository in /opt/ajenti"

git clone -b dev https://github.com/daniel-schulz/netzint-ajenti.git ajenti || exit 1
cd ajenti

msg ":: Installing Python requirements"

$PYTHON3 -m pip install -r ajenti-core/requirements.txt || exit 1

cd plugins-new
for PLUGIN in $(ls) ; do
    REQUIREMENTS_FILE=$PLUGIN/backend/requirements.txt
    if [ -f "$REQUIREMENTS_FILE" ]; then
        $PYTHON3 -m pip install -r $REQUIREMENTS_FILE || exit 1
    fi
done

msg ":: Building localization files"

ajenti-dev-multitool --msgfmt || exit 1
cd ..
msg ":: Building frontends of all plugins "
ajenti-dev-multitool --build-frontend || exit 1

msg ":: Preparing configuration files"

mkdir /etc/ajenti
echo "users: null" > /etc/ajenti/users.yml
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
trusted_domains: []
trusted_proxies: []
session_max_time: 3600
name: $(hostname)
ssl:
  certificate:
  force: false
  fqdn_certificate:
  client_auth:
    certificates: []
    enable: false
    force: false
  enable: false
EOF

msg ":: Generating self-signed certificate"

/opt/ajenti/ajenti/ajenti-panel/ajenti-ssl-gen $(hostname)


msg ':: Complete'
echo
echo 'Ajenti dev environment is fully installed :'
echo -e ' - See plugins-new/README.md to see how to start the frontend of the plugins'
echo -e ' - virtual environment is located in \e[4m/opt/ajenti\e[0m'
echo -e ' - git repository is located in \e[4m/opt/ajenti/ajenti\e[0m'
echo
echo -e 'In order to run in dev mode, activate the virtual environment : \e[92msource /opt/ajenti/bin/activate\e[39m,'
echo -e 'navigate in the git repository : \e[92mcd /opt/ajenti/ajenti\e[39m,'
echo -e 'run the backend with  a rundev recipe : \e[92m sudo make rundev\e[39m ( quit with Ctrl+ C ),'
echo -e 'and then call \e[92mhttps://localhost:8000\e[39m in your browser.'
echo 'You may receive a warning because of the self-signed certificate, it is perfectly normal.'
echo
echo -e '\e[1m\e[92mEnjoy and thank you for contributing to Ajenti !\e[39m\e[0m'
