.. _dev-getting-started:

Getting Started
***************

Required knowledge
==================

  * Python 2
  * JavaScript (ES5, ES6 or CoffeeScript)
  * basic AngularJS knowledge (modules & controllers)
  * basic HTML skills

Setting up development environent
=================================

1. Install Ajenti
-----------------

We recommend to use the automatic installer - see the :ref:`installation guide <installing>`

2. Install build tools
----------------------

Build tools require NodeJS - you can use the NodeSource repositories for quick setup::

    # Using Ubuntu
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    sudo apt-get install -y nodejs

    # Using Debian, as root
    curl -sL https://deb.nodesource.com/setup_7.x | bash -
    apt-get install -y nodejs

    # Using RHEL or centos, as root
    curl -sL https://rpm.nodesource.com/setup_7.x | bash -
    yum install nodejs

Now, install the build tools::

    npm -g install bower babel-cli babel-preset-es2015 babel-plugin-external-helpers less coffee-script angular-gettext-cli angular-gettext-tools

    # Ubuntu or Debian:
    apt-get install gettext

    # RHEL or CentOS
    yum install gettext


3. Install ajenti-dev-multitool
-------------------------------

    pip install ajenti-dev-multitool

Your first plugin
=================

    Create a new plugin in the current directory::

        ajenti-dev-multitool --new-plugin "Some plugin name"

    Build resources::

        cd some_plugin_name
        ajenti-dev-multitool --build

    And start it::

        sudo ajenti-dev-multitool --run-dev

    This will start Ajenti with the stock plugins plus the current one, and will rebuild plugin resources every time you reload Ajenti in browser.

    Navigate to http://localhost:8000/. You should see new plugin in the sidebar.


What's inside
=============

Each plugin package consists of Python modules, which contain :class:`jadi.component` classes (*components*).
Packages also may contain :ref:`static files, templates and JS and CSS code <dev-resources>`, e.g.::

      * some_plugin_name
        - plugin.yml # plugin description
        - __init__.py
        - other_python_module.py
        * resources
          * vendor
            - jquery-ui # Bower components
        * js
          - module.js # Angular.js code
          - ecmascript6-code.es
          - coffeescript-code.coffee
        * css
          - styles.css
          - styles.less
        * partials
          -- index.html


Where to go from here
=====================

Example plugins
---------------

    Download plugins from here: https://github.com/ajenti/demo-plugins or clone this entire repository.

    Prep work::

        ajenti-dev-multitool --bower install
        ajenti-dev-multitool --rebuild

    Run::

        ajenti-dev-multitool --run-dev

    .. HINT::
      Changes in ES6, CoffeeScript and LESS files will be recompiled automatically when you refresh the page; Python code will not. Additional debug information will be available in the console output and browser console. Reloading the page with Ctrl-F5 (``Cache-Control: no-cache``) will unconditionally rebuild all resources
