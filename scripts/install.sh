#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

DISTRO=
OS=

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

if grep 'CentOS' /etc/issue > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=centos
fi

if grep 'CentOS' /etc/os-release > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=centos
fi

if grep 'Red' /etc/issue > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=rhel
fi

if [ ! $OS ] ; then
    echo "Could not detect OS"
    echo "Press Enter to continue"
    read -n1
fi


echo "OS: $OS"
echo "Distro: $DISTRO"

if [ "$OS" == "rhel" ] ; then
    echo Installing prerequisites
    yum install -y gcc python-devel python-pip libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python || exit 1
fi

if [ "$OS" == "debian" ] ; then
    echo Installing prerequisites
    apt-get install -y build-essential python-pip python-dev python-lxml libffi-dev libssl-dev libjpeg-dev libpng-dev python-dbus || exit 1
fi

echo "Installing Ajenti"

pip install ajenti-panel ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins

echo "Installing initscript"

if [ -e /etc/init ] ; then
    cat << EOF > /etc/init/ajenti-panel.conf
description     "Ajenti panel"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5

expect fork

exec /usr/local/bin/ajenti-panel -d
EOF
    service ajenti-panel start

else
    if [ -e /lib/systemd/system ] ; then
        INITSCRIPT=/etc/init.d/ajenti-panel
        cat << EOF > /lib/systemd/system/ajenti-panel.service
[Unit]
Description=Ajenti panel
After=network.target

[Service]
Type=forking
PIDFile=/var/run/ajenti.pid
ExecStart=/usr/bin/ajenti-panel -d
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl start ajenti-panel
    else
        cat << EOF > $INITSCRIPT
#!/bin/sh

### BEGIN INIT INFO
# Provides:          ajenti
# Required-Start:    $network $syslog $local_fs
# Required-Stop:     $network $syslog $local_fs
# Should-Start:      $local_fs
# Should-Stop:       $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Ajenti
# Description:       Ajenti administration frontend
### END INIT INFO

if [ -e /lib/lsb/init-functions ]; then
    . /lib/lsb/init-functions

    log_success() {
        log_success_msg "$1"
    }

    log_failure() {
        log_failure_msg "$1"
    }
else
    . /etc/rc.d/init.d/functions

    log_success() {
        echo_success
        echo "$1"
    }

    log_failure() {
        echo_failure
        echo "$1"
    }
fi

NAME=Ajenti
DAEMON=/usr/bin/ajenti-panel
PIDFILE=/var/run/ajenti.pid

case "$1" in
    start)
        echo "Starting $NAME:"
        export LC_CTYPE=en_US.UTF8

        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            log_failure "already running"
            exit 1
        fi
        if $DAEMON -d ; then
            log_success "started"
        else
            log_failure "failed"
        fi
        ;;
    stop)
        echo "Stopping $NAME:"
        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            killproc -p $PIDFILE $DAEMON
            /bin/rm -rf $PIDFILE
            log_success "stopped"
        else
           log_failure "not running"
        fi
        ;;
    restart)
        $0 stop && sleep 2 && $0 start
        ;;
    status)
        if pidofproc -p $PIDFILE $DAEMON > /dev/null; then
            log_success "$NAME is running"
        else
            log_success "$NAME is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

exit 0
EOF
        $INITSCRIPT start
    fi
fi
