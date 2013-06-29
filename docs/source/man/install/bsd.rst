.. _bsd-install:

FreeBSD Installation
********************

Prerequisites::
    
    cd /usr/ports/devel/py-pip; make install clean

Download and install latest Ajenti build from PYPI::
    
    pip install ajenti

Install rc.d script::

    wget https://raw.github.com/Eugeny/ajenti/master/packaging/files/ajenti-bsd -O /etc/rc.d/ajenti