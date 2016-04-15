.. _dev-getting-started:

Getting Started with Plugin Development
***************************************

Required knowledge
==================

Building plugin backend API:

  * Python 2.x
  * async programming with gevent (optional but recommended)

Build plugin frontend:

  * CoffeeScript or JavaScript
  * basic AngularJS knowledge (modules & controllers)
  * basic HTML layout
  * CSS or LESS (optional, for custom styling)

Prerequisites
=============

The following is the absolutely minimal set of software required to build and run Ajenti:

  * Node, bower, coffee-script and lessc (from NPM)


Debian/Ubuntu extras:

  * python-dbus (ubuntu)


Setting up
==========

Install complete Ajenti bundle as outlined in the :ref:`installation guide <installing>`.

.. HINT::

    Development environment requires Node.js and NPM - if your distribution does not include a recent Node.js version, use the Nodesource repositories::

        # Ubuntu
        curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
        sudo apt-get install -y nodejs

        # Debian, as root
        curl -sL https://deb.nodesource.com/setup_5.x | bash -
        apt-get install -y nodejs

        # RHEL / CentOS
        curl -sL https://rpm.nodesource.com/setup_5.x | bash -


Install the dependencies::

    sudo pip install ajenti-dev-multitool
    sudo npm install -g coffee-script less bower angular-gettext-cli angular-gettext-tools

.. WARNING::
  We highly recommend to start with existing well-commented demo plugins instead of making ones from scratch.
  Download plugins from here: https://github.com/ajenti/demo-plugins or clone this entire repository.

  Navigate into the ``demo-plugins`` directory. Download and install Bower dependencies::

      ajenti-dev-multitool --bower install

Ensure that resource compilation is set up correctly and works (optional)::

    ajenti-dev-multitool --build

Launch Ajenti in dev mode with the plugins from the current directory::

    sudo ajenti-dev-multitool --run-dev

Navigate to http://localhost:8000/. You should see those demo plugins in the sidebar.

.. HINT::
  Changes in CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console. Reloading the page with Ctrl-F5 (``Cache-Control: no-cache``) will unconditionally rebuild all resources


Example plugins
===============

Make sure to run ``make bower`` restart Ajenti afterwards.

Plugin structure
================

Each plugin package consists of few Python modules, which contain :class:`jadi.component` classes (*components*).
Packages also may contain :ref:`static files, CoffeeScript and LESS code <dev-resources>`::


      * plugins
        * myplugin
          - plugin.yml # plugin descriptions
          - __init__.py
          * module
            - stuff.py
          - morestuff.py
          * resources
            * vendor
              - ... # Bower components
            * partial # view templates
              - index.html
              - view.html
            * js
              - module.coffee # Angular.js module
              * services # other angular components
                - some.service.coffee
            * css
                - styles.less
