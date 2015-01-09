Running Ajenti
==============

Starting service
----------------

Packages install binary *ajenti-panel* and initscript *ajenti*.
You can ensure the service is running::

    service ajenti restart

or::

    /etc/init.d/ajenti restart


Ajenti can be run in a verbose debug mode::

    ajenti-panel -v

The panel will be available on **HTTPS** port **8000** by default. The default username is **root**, and the password is **admin**

Commandline options
-------------------

  * **-c**, **--config <file>** - Use given config file instead of default
  * **-v** - Debug/verbose logging
  * **-d, --daemon** - Run in background (daemon mode)
  * **--set-platform <id>** - Override OS detection


Debugging
---------

Running ajenti with ``-v`` enables additional logging and Exconsole emergency console (see https://github.com/Eugeny/exconsole).

Exconsole can be triggered by a crash, sending SIGQUIT or pressing ``Ctrl-\`` on the controlling terminal.