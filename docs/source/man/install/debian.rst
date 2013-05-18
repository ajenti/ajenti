.. _debian-packages:

Debian Packages
***************

Add repository key::

    wget http://repo.ajenti.org/debian/key -O- | sudo apt-key add -

Install the package::
    
    apt-get update && apt-get install ajenti

Start the service::
    
    service ajenti restart
