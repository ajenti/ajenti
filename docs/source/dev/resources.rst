.. _dev-resources:

Plugin resources
****************

Basics
======

Plugin resource files are contained under ``resources`` directory nested in the plugin directory.

We encourage following structure::

    * plugin
      * resources
        * css
          - styles.less
        * js
          - module.coffee
          - routing.coffee
          * controllers
            - some.controller.coffee
          * services
            - some.service.coffee
        * img
          - image.png
        * partials
          - view.html


CSS, JS and HTML resources must be listed in the ``plugin.yml`` file in order to be served to client. Example::

    name: test
    ...
    resources:
        - 'resources/vendor/jquery/dist/jquery.min.js'  # Bower component
        - 'resources/css/animations.less'               # Styles
        - 'resources/js/core/filters.coffee'            # JS
        - 'resources/partial/index.html'                # HTML
        - 'ng:moduleName'                               # Special syntax for publishing an AngularJS module.

Please note that the last item instructs Ajenti core to load the specified AngularJS module (``test``) from the plugin.

Bower components
================

Example can be browsed and downloaded at https://github.com/ajenti/demo-plugins/tree/master/demo_3_bower

Plugins can depend on Bower components. To use this feature, create a ``bower.json`` file in your plugin directory::

    {
      "name": "plugin",
      "private": true,
      "dependencies": {
        "jquery": "~2.1.3"
      }
    }

Components are installed into ``<plugin>/resources/vendor`` directory. To install/update the components, run ``ajenti-dev-multitool --bower install``. You can also run ``make bower`` in the root of a complete Ajenti code tree to install Bower components in all plugins.

You can run other Bower commands with e.g. ``ajenti-dev-multitool --bower "list --force --verbose"``.

Resource access
===============

AngularJS templates are pre-loaded on the client. A template residing in ``plugins/test/resources/dir/template.html`` can be accessed with the following URL: ``/test:resources/dir/template.html``.

Other resource files are available through HTTP at ``/resources/<plugin_id>/resources/<path>``.

Resource compilation
====================

When running in dev mode (``--dev``), Ajenti will invoke ``ajenti-dev-multitool --build`` on page reload. Force-reloading the page (Ctrl/Cmd-F5) will rebuild all resources in all plugins using ``ajenti-dev-multitool --rebuild``

``ajenti-dev-multitool`` will automatically compile CoffeeScript and LESS code, concatenate CSS and JS specified in ``plugin.yml`` and place built CSS and JS files in ``plugin/resources/build``. Please note that ``ajenti-dev-multitool`` will only process files in the current directory and below.
