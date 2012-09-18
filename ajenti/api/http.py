import re

from ajenti.api import interface


def url(pattern):
    def decorator(f):
        f._url_pattern = re.compile('^%s$' % pattern)
        return f
    return decorator


@interface
class HttpPlugin (object):
    def handle(self, context):
        for name, method in self.__class__.__dict__.iteritems():
            if hasattr(method, '_url_pattern'):
                method = getattr(self, name)
                match = method._url_pattern.match(context.path)
                if match:
                    context.route_data = match.groupdict()
                    return method(context, **context.route_data)
