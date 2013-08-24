Installation
************

Installing packages
===================

* :ref:`Debian Packages <debian-packages>`
* :ref:`Ubuntu Packages <ubuntu-packages>`
* :ref:`RPM Packages <rpm-packages>`
* :ref:`FreeBSD (experimental) <bsd-installation>`

Please support us!
==================

Please support Ajenti by purchasing a pre-set Ajenti VPS from A2 Hosting.

.. image:: /_static/a2hosting.png

`Get an Ajenti VPS <https://affiliates.a2hosting.com/idevaffiliate.php?id=3660&url=304>`_

Running
=======

Packages install binary *ajenti-panel* and initscript *ajenti*.
You can ensure the service is running::

    service ajenti restart

or::

    /etc/init.d/ajenti restart


Ajenti can be run in a verbose debug mode::

    ajenti-panel -v

The panel will be available on **HTTPS** port **8000**. The default username is **root**, and the password is **admin**