#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

DEPRECATED_WARNING="This script will directly install Ajenti on your system which is not recommended anymore.
Please prefer the installation script with virtual environment, see: https://docs.ajenti.org/en/latest/man/install.html#automatic-installation-in-virtual-environment."
echo -e "\e[1m\e[91m$DEPRECATED_WARNING\e[39m\e[0m"

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

    msg ":: Installing prerequisites"
    apt-get update

    DEBIAN_VERSION=$(cat /etc/debian_version | cut -d'.' -f1)
    if [[ $DEBIAN_VERSION -ge 13 ]] ; then
        DEBIAN_FRONTEND='noninteractive' apt-get install -y build-essential python3-pip python3-venv python3-dev python3-lxml python3-dbus python3-augeas libssl-dev python3-apt ntpsec-ntpdate || exit 1
    else
        DEBIAN_FRONTEND='noninteractive' apt-get install -y build-essential python3-pip python3-venv python3-dev python3-lxml python3-dbus python3-augeas libssl-dev python3-apt ntpdate || exit 1
    fi
fi

msg ":: Installing node dependencies"

npm -g install bower babel-cli babel-preset-es2015 babel-plugin-external-helpers less coffee-script angular-gettext-cli angular-gettext-tools

msg ":: Setting up virtual env in /opt"

$PYTHON3 -m venv /opt/ajenti --system-site-packages
source /opt/ajenti/bin/activate
PYTHON3=/opt/ajenti/bin/python3

msg ":: Upgrading PIP"

rm /usr/lib/$PYTHON3/dist-packages/setuptools.egg-info || true # for debian 7
$PYTHON3 -m pip install -U pip wheel setuptools packaging
$PYTHON3 -m pip uninstall -y gevent-socketio gevent-socketio-hartwork

msg ":: Installing Ajenti Dev Multitool"

$PYTHON3 -m pip install ajenti-dev-multitool || exit 1

cd /opt/ajenti

msg ":: Cloning git repository in /opt/ajenti"

git clone git://github.com/ajenti/ajenti.git || exit 1
cd ajenti

msg ":: Installing Python requirements"

$PYTHON3 -m pip install -r ajenti-core/requirements.txt || exit 1

cd plugins
for PLUGIN in $(ls) ; do
    $PYTHON3 -m pip install -r $PLUGIN/requirements.txt || exit 1
done

# Temporary fix for newer versions
$PYTHON3 -m pip install gipc -U
$PYTHON3 -m pip install gevent==25.5.1
$PYTHON3 -m pip install zope.event==5.1.1

msg ":: Installing Bower dependencies"

ajenti-dev-multitool --bower install || exit 1
ajenti-dev-multitool --msgfmt || exit 1
ajenti-dev-multitool --build || exit 1

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
echo -e ' - virtual environment is located in \e[4m/opt/ajenti\e[0m'
echo -e ' - git repository is located in \e[4m/opt/ajenti/ajenti\e[0m'
echo
echo -e 'In order to run in dev mode, activate the virtual environment : \e[92msource /opt/ajenti/bin/activate\e[39m,'
echo -e 'navigate in the git repository : \e[92mcd /opt/ajenti/ajenti\e[39m,'
echo -e 'launch a rundev recipe : \e[92mmake rundev\e[39m ( quit with Ctrl+ C ),'
echo -e 'and then call \e[92mhttps://localhost:8000\e[39m in your browser.'
echo 'You may receive a warning because of the self-signed certificate, it is perfectly normal.'
echo
echo -e '\e[1m\e[92mEnjoy and thank you for contributing to Ajenti !\e[39m\e[0m'
