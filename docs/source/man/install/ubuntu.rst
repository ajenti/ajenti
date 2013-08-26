.. _ubuntu-packages:

Ubuntu Packages
***************

Please support us
=================
    
    Please support Ajenti by purchasing a reliable and fast Ajenti Ubuntu VPS from A2 Hosting!
    
    .. image:: /_static/a2hosting.png
        :target: https://affiliates.a2hosting.com/idevaffiliate.php?id=3660&url=304

Installing
==========

Ajenti requires ubuntu 12.04 Precise Pangolin. Previous releases might work with Python upgraded.

Add repository key::

    wget http://repo.ajenti.org/debian/key -O- | apt-key add -

Add repository to /etc/apt/sources.list::
    
    echo "deb http://repo.ajenti.org/ng/debian main main ubuntu" >> /etc/apt/sources.list

Install the package::
    
    apt-get update && apt-get install ajenti

Start the service::
    
    service ajenti restart
