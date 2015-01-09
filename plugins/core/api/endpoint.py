from functools import wraps
from urllib import quote
import json
import logging
import traceback


class EndpointError (Exception):
    def __init__(self, inner, message):
        self.inner = inner
        self.message = message

    def __unicode__(self):
        return self.message


def endpoint(page=False, api=False, file=False, auth=True):
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
            except Exception as e:
                logging.error('Endpoint error at %s' % context.path)
                traceback.print_exc()
                if page:
                    raise
                status = 500
                result = {
                    'message': unicode(e),
                    'exception': unicode(e.__class__.__name__),
                    'traceback': unicode(traceback.format_exc()),
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

