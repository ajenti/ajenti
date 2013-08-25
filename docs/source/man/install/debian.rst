.. _debian-packages:

Debian Packages
***************

Please support us!
==================
    
    Please support Ajenti by purchasing a pre-set Ajenti VPS from A2 Hosting.
    
    .. image:: /_static/a2hosting.png
    
    `Get an Ajenti VPS <https://affiliates.a2hosting.com/idevaffiliate.php?id=3660&url=304>`_

Installing
==========

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
