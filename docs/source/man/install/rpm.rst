.. _rpm-packages:

RPM Packages
************

Please support us
=================
    
    Please support Ajenti by purchasing a reliable and fast Ajenti CentOS VPS from A2 Hosting!
    
    .. image:: /_static/a2hosting.png
        :target: https://affiliates.a2hosting.com/idevaffiliate.php?id=3660&url=304

Installing
==========

Ajenti requires EPEL repositories: http://fedoraproject.org/wiki/EPEL

Add repository key::

    wget http://repo.ajenti.org/ajenti-repo-1.0-1.noarch.rpm
    rpm -i ajenti-repo-1.0-1.noarch.rpm

Install the package::
    
    yum install ajenti

Start the service::
    
    service ajenti restart

Package does not match intended download?
=========================================
::

    yum clean metadata