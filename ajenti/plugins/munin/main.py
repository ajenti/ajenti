from ajenti.api import *
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on, UIElement, p
from ajenti.ui.binder import Binder

import requests
import urllib2

from client import MuninClient


@plugin
class Munin (SectionPlugin):

    def init(self):
        self.title = 'Munin'
        self.icon = 'stethoscope'
        self.category = 'Software'
        self.append(self.ui.inflate('munin:main'))

        self.munin_client = MuninClient.get()
        #self.config = FSTabConfig(path='/etc/fstab')
        self.binder = Binder(None, self)
        #self.find('filesystems').new_item = lambda c: FilesystemData()

    def on_page_load(self):
        self.refresh()

    def refresh(self):
        self.munin_client.reset()
        self.binder.reset(self.munin_client).autodiscover().populate()


@plugin
class MuninProxy (HttpPlugin):
    def init(self):
        self.client = MuninClient.get()

    @url('/munin-proxy/(?P<url>.+)')
    def get_page(self, context, url):
        if context.session.identity is None:
            context.respond_redirect('/')
        url = urllib2.unquote(url)
        data = requests.get(self.client.classconfig['prefix'] + url,
                auth=(self.client.classconfig['username'], self.client.classconfig['password'])
               ).content
        context.add_header('Content-Type', 'image/png')
        context.respond_ok()
        return data


@p('url', bindtypes=[str, unicode])
@p('period')
@plugin
class MuninPlot (UIElement):
    typeid = 'munin:plot'
