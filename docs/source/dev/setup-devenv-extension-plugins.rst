.. _setup-devenv-extension-plugins:

Extension plugins
*****************

This page describes the way how to setup the development environment for the development of extension plugins.

Required knowledge
==================

  * Python 3, Typescript, Angular, HTML

Steps
=====

  * 1. Setup Ajenti (core)
  * 2. Install build tools
  * 3. Setup plugin environment


1. Setup Ajenti (core)
----------------------
The Ajenti (core) is required for the development and run of any plugin.
There are two development scenarios:

**Develop only an extension plugin**

Install the Ajenti(Core): :ref:`Installation guide <installing>`

**Develop an extension plugin + Ajenti(core) and the same time**

Run the Ajenti(Core) in the development mode :ref:`Core<setup-devenv-core>`


2. Install build tools
----------------------
Follow the steps in :ref:`Build tools<setup-devenv-build-tools>`

4. Plugin development
---------------------

4.1 Edit existing plugin
````````````````````````
See the `plugins-new/Readme.txt
<https://github.com/daniel-schulz/netzint-ajenti/blob/dev/plugins-new/README.md>`_


4.2 Create a new plugin
````````````````````````

Create a new plugin in the current directory::

    ajenti-dev-multitool --new-plugin "Some plugin name"

Build frontend::

    ajenti-dev-multitool --build-frontend

Start start the backend::

    #If Ajenti(core) was installed
    sudo ajenti-dev-multitool --run-dev
    #Navigate to http://localhost:8000/

    #If Ajenti(core) is running in the dev mode:
    make rundev


See the `plugins-new/Readme.txt to see how to start the frontend
<https://github.com/daniel-schulz/netzint-ajenti/blob/dev/plugins-new/README.md>`_


What's inside a plugin?
=======================

* Backend: Python modules, which contain :class:`jadi.component` classes (*components*).
* Frontend (optional): Angular components, services and LESS files.

Example plugin structure::

    some_plugin_name
    ├── backend/
    │   ├── controllers
    │   │   └── dashboard.py
    │   ├── __init__.py
    │   └── requirements.txt
    │
    ├── frontend/
    │   ├── e2e/
    │   └── src/
    │       ├── components
    │       │   └── uptime-widget.component.html
    │       │   └── uptime-widget.component.less
    │       │   └── uptime-widget.component.ts
    │       ├── services
    │       │   └── dashboard.service.ts
    │       └── dashboard.module.ts
    │
    ├── locale/
    ├── plugin.yml   #plugin description
    └── README.md




Example plugins
===============
See the demo-plugins git repo for some example plugin implementations.

.. warning::
    This part is obsolete. The demo-plugins repo must be converted from AngularJS to Angular.


Download plugins from here: https://github.com/ajenti/demo-plugins or clone this entire repository.

Prep work::

    ajenti-dev-multitool --build-frontend

Run::

    ajenti-dev-multitool --run-dev
