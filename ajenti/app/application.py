import traceback

#from ajenti.ui import UI
from ajenti.com import *
from ajenti.plugins import *
from ajenti.app.api import IRequestDispatcher, IContentProvider

# Base class for application/plugin infrastructure
class Application (PluginManager, Plugin):

    uri_handlers = Interface(IRequestDispatcher)
    content_providers = Interface(IContentProvider)

    content = {}

    def __init__(self, config=None):
        self.config = config
        self.log = config.get('log_facility')
        self.platform = config.get('ajenti','platform')
        # Get path for static content
        for c in self.content_providers:
            (module, path) = c.content_path()
            self.content[module] = path

    def start_response(self, status, headers=[]):
        self.status = status
        self.headers = headers

    def dispatcher(self, environ, start_response):
        self.status = '200 OK'
        self.headers = [('Content-type','text/html')]

        content = "Sorry, no content"
        for handler in self.uri_handlers:
            if handler.match(environ['PATH_INFO']):
                try:
                    content = handler.process(environ, self.start_response)
                except Exception, e:
                    self.status = '500 Error'
                    self.headers = [('Content-type', 'text/plain')]
                    content = traceback.format_exc()

        start_response(self.status, self.headers)

        return content

    def plugin_enabled(self, cls):
        if self.platform in cls.platform \
           or 'any' in cls.platform:
            return True
        return False

    def plugin_activated(self, plugin):
        plugin.log = self.log
        plugin.config = self.config
        plugin.app = self

class AppDispatcher(object):
    def __init__(self, config=None):
        self.config = config

    def dispatcher(self, environ, start_response):
        # Use unique instances for each request
        # So any plugins data will not interused between different clients 
        app = Application(self.config)

        return app.dispatcher(environ, start_response)

