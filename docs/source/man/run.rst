Running Ajenti
==============

Starting service
----------------

Ajenti provides binary *ajenti-panel* and initscript/job/unit *ajenti*.
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
  * ``--dev`` - Enables automatic resources build on each request
  * ``-d, --daemon`` - Run in background (daemon mode)
  * ``--autologin`` - Will automatically log in the user under which the panel runs. **This is a security issue if your system is public**.

Debugging
---------

Ajenti logs into ``/var/log/ajenti/ajenti.log``.

Running ajenti with ``-v`` enables additional logging.
