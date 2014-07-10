from ajenti.api import *
from ajenti.api.http import HttpPlugin, url
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on, UIElement, p
from ajenti.ui.binder import Binder

import requests
import urllib2

from client import MuninClient
from widget import MuninWidget


@plugin
class Munin (SectionPlugin):
    def init(self):
        self.title = 'Munin'
        self.icon = 'stethoscope'
        self.category = _('Software')
        self.append(self.ui.inflate('munin:main'))

        def post_graph_bind(o, c, i, u):
            for plot in u.nearest(lambda x: x.typeid == 'munin:plot'):
                plot.on('widget', self.on_add_widget, i)

        self.find('graphs').post_item_bind = post_graph_bind

        self.munin_client = MuninClient.get()
        self.binder = Binder(None, self)

    def on_page_load(self):
        self.refresh()

    def on_add_widget(self, graph, url=None, period=None):
        self.context.launch('dashboard-add-widget', cls=MuninWidget, config={'url': url, 'period': period})

    def refresh(self):
        self.munin_client.reset()
        try:
            self.munin_client.fetch_domains()
        except requests.ConnectionError as e:
            self.find_type('tabs').active = 1
            self.context.notify('error', _('Couldn\'t connect to Munin: %s') % e.message)
        except Exception as e:
            self.find_type('tabs').active = 1
            if e.message == 'auth':
                self.context.notify('error', _('Munin HTTP authentication failed'))
            else:
                raise
        self.binder.setup(self.munin_client).populate()

    @on('save-button', 'click')
    def save(self):
        self.binder.update()
        self.munin_client.save_classconfig()
        self.refresh()
        self.find_type('tabs').active = 0


@plugin
class MuninProxy (HttpPlugin):
    def init(self):
        self.client = MuninClient.get()

    @url('/ajenti:munin-proxy/(?P<url>.+)')
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
@p('widget', type=bool)
@plugin
class MuninPlot (UIElement):
    typeid = 'munin:plot'
