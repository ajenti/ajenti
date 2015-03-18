.. _dev-getting-started:

Getting Started with Plugin Development
***************************************

Prerequisites
=============

The following is the absolutely minimal set of software required to build and run Ajenti:

  * git
  * bower (from NPM)
  * coffee-script (from NPM)
  * lessc (from NPM)


Debian/Ubuntu extras:

  * python-dbus (ubuntu)


Setting up
==========

Download the source::

    git clone git://github.com/ajenti/ajenti.git

Install the dependencies::

    sudo pip install -r ajenti-core/requirements.txt
    sudo pip install ajenti-dev-multitool

Download and install Bower dependencies:

    make bower

Ensure that resource compilation is set up correctly and works (optional):

    make build

Launch Ajenti in dev mode::

    make rundev

Navigate to http://localhost:8000/.

Changes in CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console. Reloading the page with Ctrl-F5 (``Cache-Control: no-cache``) will unconditionally rebuild all resources

Ajenti source code includes various example plugins under **Demo** category; their source is available in ``ajenti/plugins/test`` directory.


Example plugins
===============

We highly recommend to start with existing well-commented demo plugins instead of making ones from scratch.
Download plugins from here: https://github.com/ajenti/demo-plugins and extract or symlink them into ``plugins`` directory.
Make sure to run ``make bower`` restart Ajenti afterwards.

Plugin structure
================

New plugins are placed in ``<source>/plugins/``.

Each plugin package consists of few Python modules, which contain :class:`ajenti.api.component` classes (*components*).
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



