from ajenti.api import *
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder

import requests
import urllib2

from client import MuninClient


@plugin
class Munin (SectionPlugin, HttpPlugin):
    default_classconfig = {
        'username': 'username',
        'password': '123',
        'prefix': 'http://localhost:8080/munin'
    }

    def init(self):
        self.title = 'Munin'
        self.icon = 'stethoscope'
        self.category = 'Software'
        self.append(self.ui.inflate('munin:main'))

        self.munin_client = MuninClient(self.classconfig)
        #self.config = FSTabConfig(path='/etc/fstab')
        self.binder = Binder(None, self)
        #self.find('filesystems').new_item = lambda c: FilesystemData()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.munin_client.reset()
        print self.munin_client.domains[0].name
        self.binder.reset(self.munin_client).autodiscover().populate()

    @url('/munin-proxy/(?P<url>.+)')
    def get_page(self, context, url):
        if context.session.identity is None:
            context.respond_redirect('/')
        url = urllib2.unquote(url)
        data = requests.get(self.classconfig['prefix'] + url,
                auth=(self.classconfig['username'], self.classconfig['password'])
               ).content
        context.add_header('Content-Type', 'image/png')
        context.respond_ok()
        return data
