.. _dev-getting-started-core:

Getting Started with Core Development
*************************************

.. ATTENTION::
   This article is only useful to the developers interested in developing the Ajenti core itself. For plugin/extension development, see :ref:`Getting started with plugin development <dev-getting-started>`

Required knowledge
==================

  * Python 2.x
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

  * python-dbus (ubuntu)


Setting up
==========

Download the source::

    git clone git://github.com/ajenti/ajenti.git

Install the dependencies::

    # Debian/Ubuntu
    sudo apt-get install build-essential python-pip python-dev python-lxml libffi-dev libssl-dev libjpeg-dev libpng-dev uuid-dev python-dbus``

    # RHEL/CentOS
    sudo yum install gcc python-devel python-pip libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python

    sudo pip install -r ajenti-core/requirements.txt
    sudo pip install ajenti-dev-multitool

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
