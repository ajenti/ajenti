.. _installing:


Installing
**********

.. CAUTION::
    Supported operating systems:

    * Debian 9 or later
    * Ubuntu Bionic or later
    * CentOS 8 or later
    * RHEL 8 or later

    Other Linux-based systems *might* work, but you'll have to use manual installation method.


Automatic Installation
======================

::

    curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install.sh | sudo bash -s -


Manual Installation
===================

Native dependencies: Debian/Ubuntu
----------------------------------

Enable Universe repository (Ubuntu only)::

    sudo add-apt-repository universe

::

    sudo apt-get install build-essential python3-pip python3-dev python3-lxml libssl-dev python3-dbus python3-augeas python3-apt ntpdate

Native dependencies: RHEL/CentOS
--------------------------------

Enable EPEL repository::

    sudo dnf install epel-release

::

    sudo dnf install -y gcc python3-devel python3-pip python3-pillow python3-augeas python3-dbus chrony openssl-devel

Install Ajenti 2
----------------

Upgrade PIP::

    sudo pip3 install setuptools pip wheel -U

Minimal install::

    sudo pip3 install ajenti-panel ajenti.plugin.core ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins

With all plugins::

    sudo pip3 install ajenti-panel ajenti.plugin.ace ajenti.plugin.augeas ajenti.plugin.auth-users ajenti.plugin.core ajenti.plugin.dashboard ajenti.plugin.datetime ajenti.plugin.filemanager ajenti.plugin.filesystem ajenti.plugin.network ajenti.plugin.notepad ajenti.plugin.packages ajenti.plugin.passwd ajenti.plugin.plugins ajenti.plugin.power ajenti.plugin.services ajenti.plugin.settings ajenti.plugin.terminal

