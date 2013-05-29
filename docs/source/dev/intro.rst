.. _dev-getting-started:

Getting Started with Plugin Development
***************************************

Prerequisites
=============

The following are the absolutely minimal set of software required to build and run Ajenti:

  * git
  * python-lxml
  * python-gevent
  * python-gevent-socketio
  * python-psutil
  * python-reconfigure (available in Ajenti repositories)
  * python-daemon
  * python-passlib
  * python-requests
  * python-imaging
  * coffee-script (use NPM)
  * lessc (use NPM)

Setting up
==========

Download the source::

    git clone git://github.com/Eugeny/ajenti.git

Launch Ajenti in debug mode::

    make run

Navigate to http://localhost:8000/.

CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console.

New plugins can be placed in both ``<source>/ajenti/plugins/`` (if you expect inclusion in the source tree) and ``/var/lib/ajenti/plugins``.

Each plugin package consists of few Python modules, which contain :class:`ajenti.api.plugin` classes.
Packages also may contain static files, CoffeeScript and LESS code, and XML user interface layouts::

    * ajenti
      * plugins
        * test
          * content
            * css
              - 1.less
            * js
              - 2.coffee
            * static
              - 3.png
          * layout
            - 4.xml
          - __init__.py
          - main.py

Continue to :ref:`Plugins <dev-plugins>`