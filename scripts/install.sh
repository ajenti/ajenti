#!/bin/bash
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

msg()
{
    message=$1
    echo
    # Bold and green font
    echo -e "\e[1m\e[92m$message\e[39m\e[0m"
    echo
}

DISTRO=
OS=
PYTHON3=$(which python3)

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

if grep 'Rocky Linux' /etc/issue > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=rockylinux
fi

if grep 'Rocky Linux' /etc/os-release > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=rockylinux
fi

if grep 'Red' /etc/issue > /dev/null 2>&1 ; then
    OS=rhel
    DISTRO=rhel
fi

if [ ! $OS ] ; then
    msg ":: Could not detect OS\n:: Press Enter to continue"
    read -n1
fi


msg ":: OS: $OS\n:: Distro: $DISTRO"

if [ "$OS" == "rhel" ] ; then
    msg ":: Installing prerequisites"
    dnf install -y epel-release
    dnf install -y gcc python3-devel python3-pip python3-pillow python3-augeas python3-dbus openssl-devel chrony redhat-lsb-core || exit 1
fi


if [ "$DISTRO" == "ubuntu" ] ; then
    msg ":: Enabling universe repository"
    add-apt-repository -y universe
fi

if [ "$OS" == "debian" ] ; then
    msg ":: Installing prerequisites"
    apt-get update
    DEBIAN_FRONTEND='noninteractive' apt-get install -y build-essential python3-pip python3-dev python3-lxml python3-dbus python3-augeas libssl-dev python3-apt ntpdate || exit 1
fi


msg ":: Upgrading PIP"

rm /usr/lib/$PYTHON3/dist-packages/setuptools.egg-info || true # for debian 7
$PYTHON3 -m pip install -U pip wheel setuptools
$PYTHON3 -m pip uninstall -y gevent-socketio gevent-socketio-hartwork

msg ":: Installing Ajenti"

$PYTHON3 -m pip install ajenti-panel ajenti.plugin.core ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins ajenti.plugin.notepad ajenti.plugin.terminal ajenti.plugin.filemanager ajenti.plugin.packages ajenti.plugin.services || exit 1

# ----------------

# Ensure /usr/local/bin is in $PATH
export PATH=$PATH:/usr/local/bin
PANEL=$(which ajenti-panel)

msg ":: Installing initscript"

if [ -e /etc/init ] && which start ; then # Upstart
    cat << EOF > /etc/init/ajenti.conf
description     "Ajenti panel"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5

expect daemon

exec $PANEL -d
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
ExecStart=$PYTHON3 $PANEL -d
ExecStartPost=/bin/sleep 5

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
PIDFILE=/var/run/ajenti.pid

case "\$1" in
    start)
        echo "Starting \$NAME:"
        export LC_CTYPE=en_US.UTF8

        if pidofproc -p \$PIDFILE \$PANEL > /dev/null; then
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
        if pidofproc -p \$PIDFILE \$PANEL > /dev/null; then
            killproc -p \$PIDFILE \$PANEL
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
        if pidofproc -p \$PIDFILE \$PANEL > /dev/null; then
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

IPADDR=$(hostname -I | awk '{$1=$1};1')

msg ':: Complete'
echo
msg "Ajenti will be listening at https://$IPADDR:8000\nLog in with your root password or another OS user"
