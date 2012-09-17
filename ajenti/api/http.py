import re

from ajenti.api import interface


def url(pattern):
    def decorator(f):
        f.__url_pattern = re.compile(pattern)
        return f
    return decorator


@interface
class HttpPlugin:
    def process_url(self, url):
        for name, method in cls.__dict__.iteritems():
            if hasattr(method, '__url_pattern'):
                match = method.__url_pattern.match(context.path)
                if match:
                    context.route_data = match.groupdict()
                    return method(context, **context.route_data)
