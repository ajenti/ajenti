Installation
************

Installing packages
===================

* :ref:`Debian Packages <debian-packages>`
* :ref:`RPM Packages <rpm-packages>`

Running
=======

Packages install binary *ajenti-panel* and initscript *ajenti*.
You can ensure the service is running::

    service ajenti restart

or::

    /etc/init.d/ajenti restart


Ajenti can be run in a verbose debug mode::

    ajenti-panel -v

The panel will be available on port **8000**. The default username is **root**, and the password is **admin**