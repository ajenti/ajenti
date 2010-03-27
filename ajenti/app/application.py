import time
import Cookie
import os.path
import hashlib
import traceback

from ajenti.com import *
from ajenti.plugins import *
from ajenti.app.session import SessionStore, SessionManager
from ajenti.app.api import IContentProvider
from ajenti.ui.api import ITemplateProvider
from ajenti.ui.template import BasicTemplate
from ajenti.app.urlhandler import IURLHandler

# Base class for application/plugin infrastructure
class Application (PluginManager, Plugin):

    uri_handlers = Interface(IURLHandler)
    content_providers = Interface(IContentProvider)
    template_providers = Interface(ITemplateProvider)

    def __init__(self, config=None):
        PluginManager.__init__(self)
        
        # Init instance variables
        self.template_path = []
        self.template_include = []
        self.content = {}
        self.config = config
        self.log = config.get('log_facility')
        self.platform = config.get('ajenti','platform')

        # Get path for static content
        for c in self.content_providers:
            (module, path) = c.content_path()
            self.content[module] = path

        # Update all template paths/includes for auto searching
        for t in self.template_providers:
            tparams = t.template()
            includes = []
            for inc in tparams['include']:
                includes.append(os.path.join(tparams['path'],inc))
            self.template_include += includes
            self.template_path += [tparams['path']]

        self.log.debug('Initialized')

    def start_response(self, status, headers=[]):
        self.status = status
        self.headers = headers

    def fix_length(self, content):
        # TODO: maybe move this method to middleware
        has_content_length = False
        for header, value in self.headers:
            if header.upper() == 'CONTENT-LENGTH':
                has_content_length = True
        if not has_content_length:
            self.headers.append(('Content-Length',str(len(content))))

    def dispatcher(self, environ, start_response):
        self.log.debug('Dispatching %s'%environ['PATH_INFO'])
        self.environ = environ
        self.status = '200 OK'
        self.headers = [('Content-type','text/html')]
        self.session = environ['app.session']

        content = "Sorry, no content"
        for handler in self.uri_handlers:
            if handler.match_url(environ):
                try:
                    self.log.debug('Calling handler for %s'%environ['PATH_INFO'])
                    content = handler.url_handler(self.environ, 
                                                  self.start_response)
                except Exception, e:
                    self.status = '500 Error'
                    self.headers = [('Content-type', 'text/plain')]
                    content = traceback.format_exc()
                finally:
                    break

        start_response(self.status, self.headers)
        self.fix_length(content)
        if not isinstance(content, environ['wsgi.file_wrapper']):
            content = [content]
        self.log.debug('Finishing %s'%environ['PATH_INFO'])
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

    def get_template(self, filename=None, search_path=[], includes=[]):
        return BasicTemplate(filename=filename, 
                             search_path=search_path+self.template_path,
                             includes=includes+self.template_include) 



class AppDispatcher(object):
    def __init__(self, config=None):
        self.config = config
        self.log = config.get('log_facility')
        # TODO: add config parameter for session timeout
        self.sessions = SessionStore()

    def dispatcher(self, environ, start_response):
        self.log.debug('Dispatching %s'%environ['PATH_INFO'])
        # Use unique instances for each request,
        # so no plugin data will be interused between different clients
        app = Application(self.config).dispatcher
        app = SessionManager(self.sessions, app)

        return app(environ, start_response)

