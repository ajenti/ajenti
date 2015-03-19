Angular: ajenti.settings
************************

Services
========

.. js:class:: settings

    .. js:function:: getConfig()

        Gets complete configuration data of the backend

        :returns: promise → global Ajenti config object

    .. js:function:: setConfig(config)

        Updates and saves configuration data

        :param object config: updated configuration data from ``getConfig()``
        :returns: promise

    .. js:function:: getUserConfig()

        Gets per-user configuration data of the backend

        :returns: promise → per-user Ajenti config object

    .. js:function:: setUserConfig(config)

        Updates and saves per-user configuration data

        :param object config: updated configuration data from ``getUserConfig()``
        :returns: promise
