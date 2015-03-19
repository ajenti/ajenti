.. _dev-ui:

User Interface
**************

Basics
======

Ajenti frontend is a AngularJS-based single-page rich web application.

Your plugins can extend it by adding new Angular components (services, controllers, directives) and routes (``ngRoute``).

Client-server communication is facilitated by AJAX requests to backend API (``$http``) and a Socket.IO connection (``socket`` and ``push`` Angular services).

Client styling is based on a customized Twitter Bootstrap build.

Example
=======

Basic UI example can be browsed and downloaded at https://github.com/ajenti/demo-plugins/tree/master/demo_2_ui

The basic UI plugin includes:

  * an AngularJS `module <https://github.com/ajenti/demo-plugins/blob/master/demo_2_ui/resources/js/module.coffee>`_ containing a `route <https://github.com/ajenti/demo-plugins/blob/master/demo_2_ui/resources/js/routing.coffee>`_ and a `controller <https://github.com/ajenti/demo-plugins/blob/master/demo_2_ui/resources/js/controllers/index.controller.coffee>`_:
  * an AngularJS `view template <https://github.com/ajenti/demo-plugins/blob/master/demo_2_ui/resources/partial/index.html>`_ (HTML)
