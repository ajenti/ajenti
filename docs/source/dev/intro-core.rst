.. _dev-getting-started-core:

Getting Started with Core Development
*************************************

.. ATTENTION::
   This article is only useful to the developers interested in developing the Ajenti core itself. For plugin/extension development, see :ref:`Getting started with plugin development <dev-getting-started>`

Required knowledge
==================

  * Python 3.x
  * async programming with gevent
  * HTML
  * CoffeeScript (with AngularJS)
  * LESS

Prerequisites
=============

The following is the absolutely minimal set of software required to build and run Ajenti:

  * git
  * bower, babel, babel-preset-es2015 and lessc (from NPM)


Debian/Ubuntu extras:

  * python3-dbus (ubuntu)

Automatic Installation
======================

The following script will perform a complete automatic installation under Debian or Ubuntu, using virtual environment with `Python`.
The virtual environment is then located in `/opt/ajenti` and the cloned git repository in `/opt/ajenti/ajenti`.
This install script will install a lot of dependencies, this may take several minutes.

::

    curl https://raw.githubusercontent.com/ajenti/ajenti/master/scripts/install-dev.sh | sudo bash -s -

After a successful installation, do the following to activate the dev mode:

 * Activate the virtual environment : `source /opt/ajenti/bin/activate`
 * Navigate in the git repository : `cd /opt/ajenti/ajenti`
 * Launch a rundev recipe : `make rundev` ( quit with Ctrl+ C )
 * Call `https://localhost:8000` in your browser ( you will get some warnings because of the self-signed certificate, it's perfectly normal.

Manual installation
===================

First, it's necessary to complete the install for plugin developpement mentioned here : :ref:`Dev getting started <dev-getting-started>`

Download the source::

    git clone git://github.com/ajenti/ajenti.git

Install the dependencies::

    # Debian/Ubuntu
    sudo apt-get install build-essential python3-pip python3-dev python3-lxml libffi-dev libssl-dev libjpeg-dev libpng-dev uuid-dev python3-dbus gettext

    # RHEL
    sudo dnf install gcc python3-devel python3-pip libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python gettext

    cd ajenti
    sudo pip3 install -r ajenti-core/requirements.txt
    sudo pip3 install ajenti-dev-multitool

    sudo npm install -g coffee-script less bower


Download and install Bower dependencies::

    make bower

Ensure that resource compilation is set up correctly and works (optional)::

    make build

Launch Ajenti in dev mode::

    make rundev

Navigate to http://localhost:8000/.

.. HINT::
  Changes in CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console. Reloading the page with Ctrl-F5 (``Cache-Control: no-cache``) will unconditionally rebuild all resources
