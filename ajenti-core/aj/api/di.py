import logging


class Context (object):
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
    def get_fqdn(cls):
        return cls.__module__ + '.' + cls.__name__

    def get_service(self, cls):
        fqdn = self.get_fqdn(cls)
        if not fqdn in self.service_instances:
            self.service_instances[fqdn] = cls(self)
        return self.service_instances[fqdn]

    def get_components(self, cls):
        for component in cls._implementations: 
            fqdn = self.get_fqdn(component)
            if not fqdn in self.component_instances:
                self.component_instances[fqdn] = component(self)
            yield self.component_instances[fqdn]


def service(cls):
    if not cls:
        return None

    # Inject methods
    def get(cls, context):
        return context.get_service(cls)
    cls.get = get.__get__(cls)

    logging.debug('Registering [%s] (service)' % Context.get_fqdn(cls))

    return cls


def interface(cls):
    if not cls:
        return None

    cls._implementations = []

    # Inject methods
    def all(cls, context):
        return list(context.get_components(cls))
    cls.all = all.__get__(cls)

    def classes(cls):
        return list(cls._implementations)
    cls.classes = classes.__get__(cls)

    logging.debug('Registering [%s] (interface)' % Context.get_fqdn(cls))

    return cls


def component(interface):
    def decorator(cls):
        if not cls:
            return None

        # Run custom verificator if any
        if hasattr(cls, '__verify__'):
            if not cls.__verify__():
                return cls

        if not hasattr(interface, '_implementations'):
            logging.error('%s is not an @interface' % interface)

        logging.debug('Registering [%s] (implementation of [%s])' % (Context.get_fqdn(cls), Context.get_fqdn(interface)))
        interface._implementations.append(cls)
        return cls

    return decorator

