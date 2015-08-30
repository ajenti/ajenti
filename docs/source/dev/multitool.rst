.. _dev-multitool:

Ajenti Dev Multitool
********************

::

    sudo pip install ajenti-dev-multitool

``ajenti-dev-multitool`` is a mini-utility to help you with common plugin development tasks.

``ajenti-dev-multitool`` typically operates on all plugins found in current directory and below.

  * ``--run`` will launch the globally installed Ajenti with plugins from the current directory. ``--run-dev`` will additionally enable developer mode.
  * ``--bower "<bower-command-with-args>"`` will run a Bower command for each plugin having its own ``bower.json`` file. Example: ``ajenti-dev-multitool --bower "install"``.
  * ``--build`` updates the resource bundles. ``--rebuild`` will discard any previously built resources.
  * ``--setuppy "<setup.py-command-with-args>"`` runs a setuptools command on the plugin package. A ``setup.py`` file is generated automatically. Example: ``ajenti-dev-multitool --setuppy 'sdist upload --sign --identity "John Doe"'``
