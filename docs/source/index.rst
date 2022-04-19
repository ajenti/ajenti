.. .. seealso::
..   * :ref:`Installing <installing>`
..   * :ref:`Architecture and how it works <architecture>`
..   * :ref:`Extension plugins <setup-devenv-extension-plugins>`
..   * :ref:`Core <setup-devenv-core>`

Ajenti
------

Ajenti is a highly extensible platform.
The core of the platform provides HTTP server, Socket engine and Plugin container.
The extensibility is implemented via a system of extension plugins.

The backend is written in Python (**Ajenti Core**).
The frontend is written in Angular application hosted in the core plugin **shell**.

For more information about the architecture see the :ref:`Architecture and how it works <architecture>`.


Feature Overview
----------------

HTTP Server
===========

* HTTP 1.1 Support.
* Websockets with fallback to XHR polling.
* Fast event-loop based processing.
* Flexible routing.
* Session sandboxing.
* SSL with client certificate authentication.

Performance
===========

* >1000 requests per second.
* 30 MB RAM footprint + 5 MB per session.

API
===

* Highly modular Python API. Everything is a module and can be removed or replaced.
* Builtin webserver API supports routing, file downloads, GZIP, websockets and more.
* Transparent SSL client authorization.
* Plugin architecture
* Dependency injection
* Server-side push and socket APIs.

Security
========

* Pluggable authentication and authorization.
* Stock authenticators: UNIX account, password, SSL client certificate and Mozilla Persona E-mail authentication.
* Unprivileged sessions isolated in separate processes.
* Fail2ban rule

Frontend
========

* Clean, modern and responsive UI. Single-page, no reloads.
* Live data updates and streaming with Socket.IO support.
* Full mobile and tablet support.
* LESS support.
* Numerous stock directives.
* Angular framework

Platforms
=========

* Debian 9 or later
* Ubuntu Bionic or later
* RHEL 8 or later
* Can be run on other Linux or BSD systems with minimal modifications.
* Supports Python 3.5+.


.. toctree::
   :maxdepth: 1
   :caption: Users
   :hidden:

   man/install.rst
   man/run.rst
   man/config.rst
   man/security.rst
   man/contributing.rst

.. toctree::
   :maxdepth: 1
   :caption: Plugins
   :hidden:

   plugins/check_certificates.rst
   plugins/core.rst
   plugins/cron.rst
   plugins/dashboard.rst
   plugins/datetime.rst
   plugins/docker.rst
   plugins/filemanager.rst
   plugins/fstab.rst
   plugins/network.rst
   plugins/notepad.rst
   plugins/packages.rst
   plugins/plugins.rst
   plugins/power.rst
   plugins/services.rst
   plugins/session_list.rst
   plugins/settings.rst
   plugins/terminal.rst
   plugins/users.rst

.. toctree::
   :maxdepth: 1
   :caption: Developers
   :hidden:

   dev/architecture.rst
   dev/multitool.rst
   dev/ui.rst
   dev/http.rst
   dev/dash-widgets.rst

.. toctree::
   :maxdepth: 1
   :caption: Setup dev. environment
   :hidden:

   dev/setup-devenv-extension-plugins.rst
   dev/setup-devenv-core.rst
   dev/setup-devenv-build-tools.rst

.. toctree::
   :maxdepth: 1
   :caption: Python API Reference
   :hidden:

   ref/jadi
   ref/aj
   ref/aj.api.http
   ref/aj.api.endpoint
   ref/aj.config
   ref/aj.core
   ref/aj.entry
   ref/aj.http
   ref/aj.plugins


.. toctree::
   :maxdepth: 1
   :caption: Stock Angular components
   :hidden:

   refjs/core
   refjs/ace
   refjs/augeas
   refjs/filesystem
   refjs/passwd
   refjs/services
   refjs/terminal


.. toctree::
   :maxdepth: 1
   :caption: Plugin API Reference
   :hidden:

   ref/aj.plugins.core.api.push
   ref/aj.plugins.core.api.sidebar
   ref/aj.plugins.core.api.tasks
   ref/aj.plugins.augeas.api
   ref/aj.plugins.auth-users.api
   ref/aj.plugins.dashboard.widget
   ref/aj.plugins.check_certificates.api
   ref/aj.plugins.datetime.api
   ref/aj.plugins.network.api
   ref/aj.plugins.packages.api
   ref/aj.plugins.power.api
   ref/aj.plugins.services.api
