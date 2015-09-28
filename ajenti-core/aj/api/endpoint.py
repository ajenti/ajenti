from functools import wraps
import json
import logging
import six
import traceback

from aj.auth import SecurityError


@six.python_2_unicode_compatible
class EndpointError(Exception):
    """
    To be raised by endpoints when a foreseen error occurs.
    This exception doesn't cause a client-side crash dialog.

    :param inner: inner exception
    :param message: message
    """
    def __init__(self, inner, message=None):
        Exception.__init__(self)
        self.inner = inner
        self.message = message or six.u(inner)
        try:
            self.traceback_str = traceback.format_exc()
        except:
            self.traceback_str = None

    def __str__(self):
        return self.message


@six.python_2_unicode_compatible
class EndpointReturn(Exception):
    """
    Raising ``EndpointReturn`` will return a custom HTTP code in the API endpoints.

    :param code: HTTP code
    :param data: response data
    """
    def __init__(self, code, data=None):
        Exception.__init__(self)
        self.code = code
        self.data = data

    def __str__(self):
        return '[EndpointReturn: %s]' % self.code


def endpoint(page=False, api=False, file=False, auth=True):
    """
    It's recommended to decorate all HTTP handling methods with ``@endpoint``.

    ``@endpoint(auth=True)`` will require authenticated session before giving control to the handler.

    ``@endpoint(api=True)`` will wrap responses and exceptions into JSON, and will also provide special handling of :class:`EndpointsError`

    :param auth: requires authentication for this endpoint
    :type  auth: bool
    :param page: enables page mode
    :type  page: bool
    :param api: enables API mode
    :type  api: bool
    """
    def decorator(fx):
        @wraps(fx)
        def wrapper(self, context, *args, **kwargs):
            if auth and not self.context.identity:
                context.respond(401)
                return ''

            status = 200

            try:
                result = fx(self, context, *args, **kwargs)
                if page:
                    return result
            except EndpointReturn as e:
                logging.debug('Endpoint return at %s: %s', context.path, e.code)
                status = e.code
                result = e.data
            except (EndpointError, SecurityError) as e:
                logging.warn('Endpoint error at %s: %s', context.path, e.message)
                if page:
                    raise
                status = 500
                result = {
                    'message': str(e.message),
                    'exception': str(e.__class__.__name__),
                    'traceback': str(getattr(e, 'traceback_str', '')),
                }
            # pylint: disable=W0703
            except Exception as e:
                logging.error('Unhandled endpoint error at %s', context.path)
                traceback.print_exc()
                if page:
                    raise
                status = 500
                result = {
                    'message': str(e),
                    'exception': str(e.__class__.__name__),
                    'traceback': str(traceback.format_exc()),
                }

            if api:
                context.add_header('Content-Type', 'application/json')
                context.respond(status)
                return json.dumps(result)
            if file:
                if len(result) == 2:
                    path, mime = result
                else:
                    path, mime = result, 'application/octet-stream'
                """
                resp = HttpResponse('', mime)
                resp['Content-Disposition'] = 'attachment; filename=%s' % os.path.split(path)[1]
                resp['X-Accel-Redirect'] = '/internal/file-stream' + path
                return resp
                """

        return wrapper

    return decorator
