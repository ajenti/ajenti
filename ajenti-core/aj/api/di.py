import logging


class Context(object):
    '''
    A dependency injection container for :func:`interface` s, :func:`service` s and :func:`component` s

    :param parent: a parent context
    :type parent: :class:`Context`
    '''

    def __init__(self, parent=None):
        self.parent = parent
        self.service_instances = {}
        self.component_instances = {}

    def __repr__(self):
        if self.parent:
            return '[Context %s (child of %s)]' % (id(self), id(self.parent))
        else:
            return '[Context %s]' % id(self)

    @staticmethod
    def get_fqdn(clz):
        '''
        Returns a fully-qualified name for the given class
        '''
        return clz.__module__ + '.' + clz.__name__

    def get_service(self, cls):
        fqdn = self.get_fqdn(cls)
        if fqdn not in self.service_instances:
            self.service_instances[fqdn] = cls(self)
        return self.service_instances[fqdn]

    def get_components(self, cls):
        for comp in cls.implementations:
            fqdn = self.get_fqdn(comp)
            if fqdn not in self.component_instances:
                self.component_instances[fqdn] = comp(self)
            yield self.component_instances[fqdn]


def service(cls):
    '''
    Marks the decorated class as a singleton ``service``.

    Injects following classmethods:

        .. py:function:: get(context)

            Returns a singleton instance of the class for given ``context``

            :param context: context to look in
            :type context: :class:`Context`
            :returns: ``cls``
    '''

    if not cls:
        return None

    # Inject methods
    def get(cls, context):
        return context.get_service(cls)
    cls.get = get.__get__(cls)

    logging.debug('Registering [%s] (service)', Context.get_fqdn(cls))

    return cls


def interface(cls):
    '''
    Marks the decorated class as an abstract interface.

    Injects following classmethods:

        .. py:function:: all(context)

            Returns a list of instances of each component in the ``context`` implementing this ``@interface``

            :param context: context to look in
            :type context: :class:`Context`
            :returns: list(``cls``)

        .. py:function:: any(context)

            Returns a first suitable instance implementing this ``@interface``

            :param context: context to look in
            :type context: :class:`Context`
            :returns: ``cls``

        .. py:function:: classes()

            Returns a list of classes implementing this ``@interface``

            :returns: list(class)
    '''

    if not cls:
        return None

    cls.implementations = []

    # Inject methods
    def _all(cls, context):
        return list(context.get_components(cls))
    cls.all = _all.__get__(cls)

    def _any(cls, context):
        return (cls.all(context) + [None])[0]
    cls.any = _any.__get__(cls)

    def _classes(cls):
        return list(cls.implementations)
    cls.classes = _classes.__get__(cls)

    logging.debug('Registering [%s] (interface)', Context.get_fqdn(cls))

    return cls


def component(iface):
    '''
    Marks the decorated class as a component implementing the given ``iface``

    :param iface: the interface to implement
    :type iface: :func:`interface`
    '''

    def decorator(cls):
        if not cls:
            return None

        # Run custom verificator if any
        if hasattr(cls, '__verify__'):
            if not cls.__verify__():
                return cls

        if not hasattr(iface, 'implementations'):
            logging.error('%s is not an @interface', iface)

        logging.debug(
            'Registering [%s] (implementation of [%s])' % (
                Context.get_fqdn(cls),
                Context.get_fqdn(iface)
            )
        )
        iface.implementations.append(cls)
        return cls

    return decorator
