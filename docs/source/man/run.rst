Running Ajenti
==============

Starting service
----------------

The automatic install script provides binary *ajenti-panel* and initscript/job/unit *ajenti*.
You can ensure the service is running::

    service ajenti restart

or::

    /etc/init.d/ajenti restart

or::

    systemctl restart ajenti


The panel will be available on **HTTPS** port **8000** by default. The default username is **root**, and the password is your system's root password.

Ajenti can also be run in a verbose debug mode::

    ajenti-panel -v

Commandline options
-------------------

  * ``-c``, ``--config <file>`` - Use given config file instead of default
  * ``-v`` - Debug/verbose logging
  * ``--log <level>`` - Fix log level : debug, info, warning or error
  * ``--dev`` - Enables automatic resources build on each request
  * ``-d, --daemon`` - Run in background (daemon mode)
  * ``--stock-plugins`` - Run with provided plugins (default if option ``--plugins`` is not used)
  * ``--plugins <dir>`` - Run with additional plugins
  * ``--autologin`` - Will automatically log in the user under which the panel runs. **This is a security issue if your system is public**.

Debugging
---------

If Ajenti does not start as intended, there are various ways to debug this, but it is good to know that the problem can have an origin in Python code or in Javascript code.

Debug Python problems
---------------------

First of all, have a look at::

    /var/log/ajenti/ajenti.log


It may contain some running errors which could be useful to understand the problem.

The traceback of a total crash would be stored in::

   /var/log/ajenti/crash-DATE.log

If this log files do not provide enough informations, you can manually start Ajenti in debug mode as root::

    systemctl stop ajenti
    /usr/local/bin/ajenti-panel -v

This will increase the verbosity of Ajenti in ``/var/log/ajenti/ajenti.log``, but you can also directly follow the progress of Ajenti start with::

    systemctl stop ajenti
    /usr/local/bin/ajenti-panel --dev

and then stop it as usual with Ctrl + C.
Don't forget after this to restart the Ajenti process if necessary::

    systemctl start ajenti

Debug Javascript problems
-------------------------

The best way to do it is to launch the developer tools in your browser, usually with F12, and to look if some errors are shown.

Submit the errors
-----------------

The best way to help the development of Ajenti is then to submit the errors at https://github.com/ajenti/ajenti/issues/new with all informations ( traceback, OS, Python version, ... ).
