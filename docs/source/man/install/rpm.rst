.. _rpm-packages:

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
