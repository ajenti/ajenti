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
        templ = self.app.get_template('uzuri.xml')
        templ.appendChildInto('sidepane', UzuriMaster().get_sidepane())
        templ.appendChildInto('mainpane', UzuriMaster().get_mainpane())
        return templ.render()

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
            htr.putrequest('GET', url)

            for h in req:
                htr.putheader(h, req[h])
            htr.endheaders()

            resp = htr.getresponse()
            start_response("%i %s" % (resp.status, resp.reason), resp.getheaders())
            return req['wsgi.file_wrapper'](resp)
        except:
            start_response("404 Not Found", [])
            return ''
