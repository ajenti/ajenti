import os
import gzip
import cgi
import math
import gevent
from StringIO import StringIO
from datetime import datetime

from socketio.handler import SocketIOHandler


def _validate_origin(env):
    valid_origin = '%s://%s' % (env['wsgi.url_scheme'], env['HTTP_HOST'])
    request_origin = env.get('HTTP_ORIGIN', '').strip('/')
    if request_origin:
        if request_origin != valid_origin:
            return False
    return True


class RootHttpHandler (SocketIOHandler):
    def handle_one_response(self):
        if not _validate_origin(self.environ):
            return super(SocketIOHandler, self).handle_one_response()
        return SocketIOHandler.handle_one_response(self)


class HttpRoot (object):
    """
    A root middleware object that creates the :class:`HttpContext` and dispatches it to other registered middleware
    """

    def __init__(self, stack=[]):
        self.stack = stack

    def add(self, middleware):
        """
        Pushes the middleware onto the stack
        """
        self.stack.append(middleware)

    def dispatch(self, env, start_response):
        """
        Dispatches the WSGI request
        """
        if not _validate_origin(env):
            start_response('403 Invalid Origin', [])
            return ''

        context = HttpContext(env, start_response)
        for middleware in self.stack:
            output = middleware.handle(context)
            if output is not None:
                return output


class HttpContext (object):
    """
    Instance of :class:`HttpContext` is passed to all HTTP handler methods

    .. attribute:: env

        WSGI environment dict

    .. attribute:: path

        Path segment of the URL

    .. attribute:: headers

        List of HTTP response headers

    .. attribute:: response_ready

        Indicates whether a HTTP response has already been submitted in this context

    .. attribute:: query

        HTTP query parameters
    """

    def __init__(self, env, start_response):
        self.start_response = start_response
        self.env = env
        self.path = env['PATH_INFO']
        self.headers = []
        self.response_ready = False

        self.env.setdefault('QUERY_STRING', '')
        if self.env['REQUEST_METHOD'].upper() == 'POST':
            ctype = self.env.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
            if ctype.startswith('application/x-www-form-urlencoded') \
               or ctype.startswith('multipart/form-data'):
                sio = StringIO(self.env['wsgi.input'].read())
                self.query = cgi.FieldStorage(fp=sio, environ=self.env, keep_blank_values=1)
            else:
                self.body = self.env['wsgi.input'].read()
        else:
            self.query = cgi.FieldStorage(environ=self.env, keep_blank_values=1)

    def add_header(self, key, value):
        """
        Adds a given HTTP header to the response

        :type key: str
        :type value: str
        """
        self.headers += [(key, value)]

    def remove_header(self, key):
        """
        Removed a given HTTP header from the response

        :type key: str
        """
        self.headers = filter(lambda h: h[0] != key, self.headers)

    def fallthrough(self, handler):
        """
        Executes a ``handler`` in this context

        :returns: handler-supplied output
        """
        return handler.handle(self)

    def respond(self, status):
        """
        Creates a response with given HTTP status line
        :type status: str
        """
        self.start_response(status, self.headers)
        self.response_ready = True

    def respond_ok(self):
        """
        Creates a ``HTTP 200 OK`` response
        """
        self.respond('200 OK')

    def respond_server_error(self):
        """
        Returns a HTTP ``500 Server Error`` response
        """
        self.respond('500 Server Error')
        return 'Server Error'

    def respond_forbidden(self):
        """
        Returns a HTTP ``403 Forbidden`` response
        """
        self.respond('403 Forbidden')
        return 'Forbidden'

    def respond_not_found(self):
        """
        Returns a ``HTTP 404 Not Found`` response
        """
        self.respond('404 Not Found')
        return 'Not Found'

    def redirect(self, url):
        """
        Returns a ``HTTP 302 Found`` redirect response with given ``url``
        :type url: str
        """
        self.add_header('Location', url)
        self.respond('302 Found')
        return ''

    def gzip(self, content, compression=9):
        """
        Returns a GZip compressed response with given ``content`` and correct headers
        :type content: str
        :type compression: int
        :rtype: str
        """
        io = StringIO()
        gz = gzip.GzipFile('', 'wb', compression, io)
        gz.write(content)
        gz.close()
        compressed = io.getvalue()

        self.add_header('Content-Length', str(len(compressed)))
        self.add_header('Content-Encoding', 'gzip')
        self.respond_ok()

        return compressed

    def file(self, path, stream=False):
        """
        Returns a GZip compressed response with content of file located in ``path`` and correct headers
        :type path: str
        :type stream: bool
        """

        # Block path traversal
        if '..' in path:
            self.respond_forbidden()
            return

        if not os.path.isfile(path):
            self.respond_not_found()
            return

        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.woff': 'application/x-font-woff',
        }

        ext = os.path.splitext(path)[1]
        if ext in content_types:
            self.add_header('Content-Type', content_types[ext])
        else:
            self.add_header('Content-Type', 'application/octet-stream')

        mtime = datetime.utcfromtimestamp(math.trunc(os.path.getmtime(path)))

        rtime = self.env.get('HTTP_IF_MODIFIED_SINCE', None)
        if rtime:
            try:
                rtime = datetime.strptime(rtime, '%a, %b %d %Y %H:%M:%S GMT')
                if mtime <= rtime:
                    self.respond('304 Not Modified')
                    return
            except:
                pass

        range = self.env.get('HTTP_RANGE', None)
        rfrom = rto = None
        if range and range.startswith('bytes'):
            rsize = os.stat(path).st_size
            rfrom, rto = range.split('=')[1].split('-')
            rfrom = int(rfrom) if rfrom else 0
            rto = int(rto) if rto else (rsize - 1)
        else:
            rfrom = 0
            rto = 999999999

        self.add_header('Last-Modified', mtime.strftime('%a, %b %d %Y %H:%M:%S GMT'))
        self.add_header('Accept-Ranges', 'bytes')

        if stream:
            if rfrom:
                self.add_header('Content-Length', str(rto - rfrom + 1))
                self.add_header('Content-Range', 'bytes %i-%i/%i' % (rfrom, rto, rsize))
                self.respond('206 Partial Content')
            else:
                self.respond_ok()
            fd = os.open(path, os.O_RDONLY)# | os.O_NONBLOCK)
            os.lseek(fd, rfrom or 0, os.SEEK_SET)
            bufsize = 100 * 1024
            read = rfrom
            buf = 1
            while buf:
                buf = os.read(fd, bufsize)
                gevent.sleep(0)
                if read + len(buf) > rto:
                    buf = buf[:rto + 1 - read]
                yield buf
                read += len(buf)
                if read >= rto:
                    break
            os.close(fd)
        else:
            yield self.gzip(open(path).read())


class HttpHandler (object):
    """
    Base class for everything that can process HTTP requests
    """

    def handle(self, context):
        """
        Should create a HTTP response in the given ``context`` and return the plain output

        :param context: HTTP context
        :type  context: :class:`ajenti.http.HttpContext`
        """
