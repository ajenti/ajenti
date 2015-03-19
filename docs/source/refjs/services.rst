Angular: ajenti.services
************************

Services
========

.. js:class:: services

    .. js:function:: getManagers()

        :returns: promise → array of the available service managers

    .. js:function:: getServices(managerId)

        :returns: promise → array of the available services in the ``ServiceManager``

    .. js:function:: getService(managerId, serviceId)

        :returns: promise → object, gets a single service from the manager

    .. js:function:: runOperation(managerId, serviceId, operation)

        :param string operation: typically ``start``, ``stop``, ``restart``, ``reload``; depends on the service manager
        :returns: promise
