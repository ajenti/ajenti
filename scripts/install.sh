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
    echo ":: Could not detect OS"
    echo ":: Press Enter to continue"
    read -n1
fi


echo ":: OS: $OS"
echo ":: Distro: $DISTRO"

if [ "$OS" == "rhel" ] ; then
    echo ":: Installing prerequisites"
    dnf install -y epel-release
    dnf install -y gcc python3-devel python3-pip python3-pillow python3-augeas python3-dbus openssl-devel chrony || exit 1
fi


if [ "$DISTRO" == "ubuntu" ] ; then
    echo ":: Enabling universe repository"
    add-apt-repository universe
fi

if [ "$OS" == "debian" ] ; then
    echo ":: Installing prerequisites"
    apt-get update
    DEBIAN_FRONTEND='noninteractive' apt-get install -y build-essential python3-pip python3-dev python3-lxml python3-dbus python3-augeas libssl-dev python3-apt ntpdate || exit 1
fi


echo ":: Upgrading PIP"
rm /usr/lib/`which python3`/dist-packages/setuptools.egg-info || true # for debian 7
`which python3` -m pip install -U pip wheel setuptools
`which python3` -m pip uninstall -y gevent-socketio gevent-socketio-hartwork

echo ":: Installing Ajenti"
`which python3` -m pip install ajenti-panel ajenti.plugin.core ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins ajenti.plugin.notepad ajenti.plugin.terminal ajenti.plugin.filemanager ajenti.plugin.packages ajenti.plugin.services || exit 1

# ----------------

echo ":: Installing initscript"

if [ -e /etc/init ] && which start ; then # Upstart
    cat << EOF > /etc/init/ajenti.conf
description     "Ajenti panel"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5

expect daemon

exec $(which ajenti-panel) -d
EOF
    start ajenti

else
    if [ -e /lib/systemd/system ] && which systemctl ; then # systemd
        cat << EOF > /lib/systemd/system/ajenti.service
[Unit]
Description=Ajenti panel
After=network.target

[Service]
Type=forking
PIDFile=/var/run/ajenti.pid
ExecStart=$(which python3) $(which ajenti-panel) -d

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable ajenti
        systemctl start ajenti
    else # sysvinit
        INITSCRIPT=/etc/init.d/ajenti
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
        log_success_msg "\$1"
    }

    log_failure() {
        log_failure_msg "\$1"
    }
else
    . /etc/rc.d/init.d/functions

    log_success() {
        echo_success
        echo "\$1"
    }

    log_failure() {
        echo_failure
        echo "\$1"
    }
fi

NAME=Ajenti
DAEMON=$(which ajenti-panel)
PIDFILE=/var/run/ajenti.pid

case "\$1" in
    start)
        echo "Starting \$NAME:"
        export LC_CTYPE=en_US.UTF8

        if pidofproc -p \$PIDFILE \$DAEMON > /dev/null; then
            log_failure "already running"
            exit 1
        fi
        if \$DAEMON -d ; then
            log_success "started"
        else
            log_failure "failed"
        fi
        ;;
    stop)
        echo "Stopping \$NAME:"
        if pidofproc -p \$PIDFILE \$DAEMON > /dev/null; then
            killproc -p \$PIDFILE \$DAEMON
            /bin/rm -rf \$PIDFILE
            log_success "stopped"
        else
           log_failure "not running"
        fi
        ;;
    restart)
        \$0 stop && sleep 2 && \$0 start
        ;;
    status)
        if pidofproc -p \$PIDFILE \$DAEMON > /dev/null; then
            log_success "\$NAME is running"
        else
            log_success "\$NAME is not running"
        fi
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status}"
        exit 1
esac

exit 0
EOF
        chmod +x $INITSCRIPT
        $INITSCRIPT start
    fi
fi

echo ':: Complete'
echo
echo 'Ajenti will be listening at HTTP port 8000'
echo 'Log in with your root password or another OS user'
