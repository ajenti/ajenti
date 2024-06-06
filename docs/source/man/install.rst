.. _installing:

Installing
**********

.. CAUTION::
    Supported operating systems:

    * Debian 9 or later
    * Ubuntu Bionic or later
    * RHEL 8 or later

    Other Linux-based systems *might* work, but you'll have to use manual installation method.


Automatic Installation
======================

This installation method will not work under Debian, prefer the virtual environment installation below.
This should work for all other operating systems.

::

    curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install.sh | sudo bash -s -

Automatic Installation in  virtual environment
==============================================


::

    curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install-venv.sh | sudo bash -s -

Manual Installation
===================

Native dependencies: Debian/Ubuntu
----------------------------------

Enable Universe repository (Ubuntu only)::

    sudo add-apt-repository universe

::

    sudo apt-get install build-essential python3-pip python3-dev python3-lxml libssl-dev python3-dbus python3-augeas python3-apt ntpdate

Native dependencies: RHEL
-------------------------

Enable EPEL repository::

    sudo dnf install epel-release

::

    sudo dnf install -y gcc python3-devel python3-pip python3-pillow python3-augeas python3-dbus chrony openssl-devel redhat-lsb-core

Install Ajenti 2
----------------

Upgrade PIP::

    sudo pip3 install setuptools pip wheel -U

Minimal install::

    sudo pip3 install ajenti-3-panel ajenti-3.plugin.shell ajenti-3.plugin.dashboard

With all plugins::

    sudo pip3 install ajenti-3-panel \
                      ajenti-3.plugin.shell \
                      ajenti-3.plugin.dashboard \
                      ajenti-3.plugin.fstab \
                      ajenti-3.plugin.lmn-theme \
                      ajenti-3.plugin.session-list \
                      ajenti-3.plugin.traffic

Uninstall Ajenti 2
==================

Ajenti is a collection of Python modules installed with pip, delivered with an init script ( systemd or sysvinit ). So it's necessary to remove the init script, then the Python librairies, and the configurations files.

Systemd
-------

::

    sudo systemctl stop ajenti.service
    sudo systemctl disable ajenti.service
    sudo systemctl daemon-reload
    sudo rm -f /lib/systemd/system/ajenti.service


SysVinit
--------

::

    /etc/init.d/ajenti stop
    rm -f /etc/init/ajenti.conf

Python3 modules
---------------

List all modules from Ajenti::

    sudo pip3 list | grep aj

The result should be something like ( eventually more or less plugins )::

    aj-3                            3.0.0
    ajenti-3-panel                  3.0.0
    ajenti-3.plugin.shell           0.1.0
    ajenti-3.plugin.dashboard       0.1.0
    ajenti-3.plugin.traffic         0.1.0
    ajenti-3.plugin.fstab           0.1.0
    ajenti-3.plugin.session-list    0.1.0

Then simply remove all these modules::

    sudo pip3 uninstall -y aj-3 \
                           ajenti-3-panel \
                           ajenti-3.plugin.shell \
                           ajenti-3.plugin.dashboard \
                           ajenti-3.plugin.traffic \
                           ajenti-3.plugin.fstab \
                           ajenti-3.plugin.session-list

Configuration files
-------------------

If you don't need it for later, just delete the directory `/etc/ajenti/`::

   sudo rm -rf /etc/ajenti/

