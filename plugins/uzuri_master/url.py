import os
from httplib import *

from ajenti.com import *
from ajenti.ui.template import BasicTemplate
from ajenti.app.helpers import EventProcessor, event
from ajenti.app.urlhandler import URLHandler, url
from ajenti.utils import shell, wsgi_serve_file

from main import *


class UzuriMasterDispatcher(URLHandler, EventProcessor, Plugin):

    @url('^/uzuri/$')
    def process(self, req, start_response):
        master = self.app.grab_plugins(IUzuriMaster)[0]
        master.init()
        templ = self.app.get_template('uzuri.xml')
        templ.appendChildInto('plugins', master.get_ui_plugins())
        templ.appendChildInto('hosts', master.get_ui_hosts())
        templ.appendChildInto('mainpane', master.get_mainpane())
        return templ.render()

    @url('^/uzuri/setcookie/.+')
    def setcookie(self, req, start_response):
        master = self.app.grab_plugins(IUzuriMaster)[0]
        master.init()
        path = req['PATH_INFO'].split('/')
        master._cookies[path[3]] = path[4]
        return ''

    @url('^/uzuri/addhost')
    def add_host(self, req, start_response):
        master = self.app.grab_plugins(IUzuriMaster)[0]
        master.init()
        master.add_host(req['QUERY_STRING'][5:])
        return self.process(req, start_response)

    @url('^/uzuri/delhost')
    def del_host(self, req, start_response):
        master = self.app.grab_plugins(IUzuriMaster)[0]
        master.init()
        master.del_host(req['QUERY_STRING'][5:])
        return self.process(req, start_response)

    @url('^/uzurigate/.+')
    def gateway(self, req, start_response):
        try:
            path = req['PATH_INFO'].split('/')
            host = path[2]
            port = 80
            if ':' in host:
                host, port = host.split(':')
            url = '/' + '/'.join(path[3:])

            htr = HTTPConnection(host=host, port=port)
            htr.connect()

            hdrs = {}
            for h in req:
                if h.startswith('HTTP') and h != 'HTTP_COOKIE':
                    hdrs[h[5:].lower().replace('_', '-')] = req[h]
                if h == 'CONTENT_TYPE':
                    hdrs['Content-type'] = req[h]

            body = None

            if (req['REQUEST_METHOD'] == 'POST'):
                body = str(req['wsgi.input'].readline())
            htr.request(req['REQUEST_METHOD'], url, body, hdrs)

            resp = htr.getresponse()
            hdrs = resp.getheaders()
            for x in hdrs:
                if x[0] == 'set-cookie':
                    hdrs.append(('X-Uzuri-Cookie', x[1].split(' ')[0]))
            start_response("%i %s" % (resp.status, resp.reason), hdrs)
            return req['wsgi.file_wrapper'](resp)
        except:
            start_response("404 Not Found", [])
            return ''
