import logging


class Context(object):
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
    if not cls:
        return None

    # Inject methods
    def get(cls, context):
        return context.get_service(cls)
    cls.get = get.__get__(cls)

    logging.debug('Registering [%s] (service)', Context.get_fqdn(cls))

    return cls


def interface(cls):
    if not cls:
        return None

    cls.implementations = []

    # Inject methods
    def _all(cls, context):
        return list(context.get_components(cls))
    cls.all = _all.__get__(cls)

    def _classes(cls):
        return list(cls.implementations)
    cls.classes = _classes.__get__(cls)

    logging.debug('Registering [%s] (interface)', Context.get_fqdn(cls))

    return cls


def component(iface):
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
