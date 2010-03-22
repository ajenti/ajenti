import os.path

from ajenti.com import *
from ajenti.app.api import IContentProvider

class WSGIDispatcher(object):
    """ WSGI middleware interface
    Could be used to stack different middlewares
    """
    def __init__(self, next_dispatcher=None):
        self.next = next_dispatcher
        self.headers = []
        self.status = '200 OK'

    def prepare(self, env):
        pass

    def start_response(self, status, headers):
        self.status = status
        self.headers.extend(headers)

    def dispatcher(self, env, start_response):
        # Call prepare to init anything
        self.prepare(env)
        # Call next dispatcher
        res = 'Empty dispatcher!'
        if self.next is not None:
            res = self.next.dispatcher(env, self.start_response)

        # Call upper response and return content
        start_response(self.status, self.headers)
        return res

class ModuleContent(Plugin):
    abstract = True
    implements(IContentProvider)

    def content_path(self):
        if self.path == '' or self.module == '':
            raise AttributeError('You should provide path/module information')  
        norm_path = os.path.join(os.path.dirname(self.path),'files')
        return (self.module, norm_path)

