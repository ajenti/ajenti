.. _setup-devenv-core:

Core
****

This page describes the way how to setup the development environment for the development of the core.

.. ATTENTION::
    For plugin/extension development see :ref:`Extension plugins <setup-devenv-extension-plugins>`

Required knowledge
=================

  * Python 3.x, async programming with gevent, HTML, Angular, Typescript, LESS

Prerequisites
=============

Minimal set of software required to build and run Ajenti: ``git``, ``Node.js``

Debian/Ubuntu extras: ``python3-dbus (ubuntu)``


Steps
=====
There are two ways how to setup the core.

    * Automatic (Recommended)
    * Manual


Automatic Installation (Backend + Frontend)
===========================================

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


Manual installation - Backend
=============================

Download the source code::

    git clone git://github.com/ajenti/ajenti.git

Install the dependencies::

    # Debian/Ubuntu
    sudo apt-get install build-essential python3-pip python3-dev python3-lxml libffi-dev libssl-dev libjpeg-dev libpng-dev uuid-dev python3-dbus

    # RHEL
    sudo dnf install gcc python3-devel python3-pip libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python

    cd ajenti
    sudo pip3 install -r ajenti-core/requirements.txt
    sudo pip3 install ajenti-dev-multitool

Install the build tools

    Follow: :ref:`Build tools <setup-devenv-build-tools>`

Ensure that resource compilation is set up correctly and works (optional)::

    make build

Launch Ajenti backend in dev mode::

    make rundev

Navigate to http://localhost:8000/.

.. HINT::
  Additional debug information will be available in the console output and browser console.
  Reloading the page with Ctrl-F5 (``Cache-Control: no-cache``) will unconditionally rebuild all resources


Manual installation - Frontend
==============================

The setup the core frontend is needed to build and run the plugins: ``ngx-ajenti`` and ``shell``

The way how to do it is described here in the plugins-new/README.md
See the Readme https://github.com/daniel-schulz/netzint-ajenti/blob/dev/plugins-new/README.md

For more info see :ref:`What’s Ajenti and how it works <man-about>`.



