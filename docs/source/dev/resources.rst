.. _dev-resources:

Plugin resources
****************

Plugin resource files are contained under ``content`` directory nested in the plugin directory. The ``content`` directory can optionally contain ``css``, ``js`` and ``static`` directories holding files of respective types.

Ajenti will accept following filename extensions. ``injected`` resources will be added to ``<head>`` of web UI. ``cleaned`` resources will be deleted before build. ``compile`` resources will be pre-processed using applicable compiler.

  * ``/content/js/*.js`` - source JS (compile)
  * ``/content/css/*.css`` - source JS (compile)
  * ``/content/js/*.coffee`` - source CoffeeScript (compile)
  * ``/content/css/*.less`` - source LESS (compile)
  * ``/content/css/*.i.less`` - source LESS included somewhere else (ignored)
  * ``/content/js/*.m.js`` - pre-built JS (injected)
  * ``/content/css/*.m.css`` - pre-built CSS (injected)
  * ``/content/js/*.c.js`` - compiled JS (injected, cleaned)
  * ``/content/css/*.c.css`` - compiled CSS (injected, cleaned)

Resources under ``/static/`` are served over HTTP at the following URL: ``/ajenti:static/<plugin-name>/<resource-path>``, e.g.: ``/ajenti:static/main/favicon.png``.