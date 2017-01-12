.. _installing:

Installation
============

Debian Packages
***************

Ajenti requires Debian 6 or later. Debian 5 might work with Python 2.6 installed.

Debian Squeeze requires squeeze-backports repository: http://backports.debian.org/Instructions/

Add repository key::

    wget http://repo.ajenti.org/debian/key -O- | apt-key add -

Add repository to /etc/apt/sources.list::

    echo "deb http://repo.ajenti.org/debian main main debian" >> /etc/apt/sources.list

Install the package::

    apt-get update && apt-get install ajenti

Start the service::

    service ajenti restart


Ubuntu Packages
***************

Ajenti requires ubuntu 12.04 Precise Pangolin. Previous releases might work with Python upgraded.

Add repository key::

    wget http://repo.ajenti.org/debian/key -O- | apt-key add -

Add repository to /etc/apt/sources.list::

    echo "deb http://repo.ajenti.org/ng/debian main main ubuntu" >> /etc/apt/sources.list

Install the package::

    apt-get update && apt-get install ajenti

Start the service::

    service ajenti restart



RPM Packages
************

Ajenti requires EPEL repositories: http://fedoraproject.org/wiki/EPEL

Add repository key::

    wget http://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm
    rpm -i ajenti-repo-1.0-1.noarch.rpm

Install the package::

    yum install ajenti

Start the service::

    service ajenti restart

.. note::
    Package does not match intended download? ::

        yum clean metadata


FreeBSD Installation
********************

Tested on FreeBSD 11.0-RELEASE.

Prerequisites::

    pkg install py27-pip py27-pillow py27-lxml py27-ldap

Download and install latest Ajenti build from PYPI::

    pip install ajenti

Download the latest Ajenti configuration file::

    mkdir -p /usr/local/etc/ajenti/
    fetch --no-verify-peer -o /usr/local/etc/ajenti/config.json https://raw.githubusercontent.com/ajenti/ajenti/1.x/packaging/files/config.json

Install rc.d script::

    mkdir -p /usr/local/etc/rc.d/
    fetch --no-verify-peer -o /usr/local/etc/rc.d/ajenti https://raw.github.com/ajenti/ajenti/1.x/packaging/files/ajenti-bsd
    chmod 555 /usr/local/etc/rc.d/ajenti

Start the Ajenti service::

    service ajenti start
