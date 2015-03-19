Angular: ajenti.terminal
************************

Services
========

.. js:class:: terminals

    .. js:function:: list()

        :returns: promise → array of opened terminal descriptors

    .. js:function:: kill(terminalId)

        Kills a running terminal process

        :returns: promise

    .. js:function:: create(options)

        Creates a new terminal

        :param string options.command:
        :param boolean options.autoclose:
        :returns: promise → new terminal ID

    .. js:function:: full(terminalId)

        :returns: promise → full content of the requested terminal
