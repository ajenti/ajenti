.. _installing:


Installing
**********

.. CAUTION::
    Supported operating systems:

    * Debian 6 or later
    * Ubuntu Precise or later
    * CentOS 6 or later
    * RHEL 6 or later

    Other Linux-based systems *might* work, but you'll have to use manual installation method.


Automatic Installation
======================

::

    curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install.sh | sudo bash -s -


Manual Installation
===================

Native dependencies: Debian/Ubuntu
----------------------------------

::

    sudo apt-get install build-essential python-pip python-dev python-lxml libffi-dev libssl-dev libjpeg-dev libpng-dev uuid-dev python-dbus

Native dependencies: RHEL/CentOS
--------------------------------

::

    sudo yum install gcc python-devel python-pip libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python

Install Ajenti
--------------

Upgrade PIP::

    sudo pip install 'setuptools>=0.6rc11' 'pip>=6' wheel

Minimal install::

    sudo pip install ajenti-panel ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins

With more plugins::

    sudo pip install ajenti-panel ajenti.plugin.dashboard ajenti.plugin.settings ajenti.plugin.plugins ajenti.plugin.filemanager ajenti.plugin.notepad ajenti.plugin.packages ajenti.plugin.services ajenti.plugin.terminal

Install Ajenti RHEL/CentOS 6.x
======================
Adding EPEL repo

rpm -ivh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm 

Adding Ajenti repo

rpm -ivh http://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm

Installing package

yum install ajenti -y

Because file is not signed you might need to append --nogpgcheck to the yum install command

Default user: root
Default password: admin

Install Ajenti 1.x and Ajenti V
======================
https://support.ajenti.org/knowledge-bases/5-kb/categories/1-ajenti-v/articles
