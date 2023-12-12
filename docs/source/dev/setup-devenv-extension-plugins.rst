.. _setup-devenv-extension-plugins:

Extension plugins
*****************

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




How to create a new plugin
==========================
Use the Ajenti Dev Multi Tool to create a new plugin from a plugin template.
Execute the `python3 scripts/ajenti-dev-multitool/ajenti_dev_multitool.py` to see documentation.
After the new plugin is created follow the standard instruction for running a plugin (README.md).
