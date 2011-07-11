from ajenti.ui import *
from ajenti.plugins.dashboard.api import *
from ajenti.com import implements, Plugin
from ajenti.api import *
from updater import Updater


class NewsWidget(Plugin):
    implements(IDashboardWidget)
    title = 'Project news'
    icon = '/dl/core/ui/stock/news.png'
    name = 'Project news'
    style = 'normal'

    def get_ui(self, cfg, id=None):
        ui = self.app.inflate('core:news')
        feed = Updater.get().get_feed()
        if feed is not None:
            for i in feed.entries[:1]:
                self.title = i.title
                ui.append('list', UI.CustomHTML(html=i.content[0].value))
        return ui

    def handle(self, event, params, cfg, vars=None):
        pass

    def get_config_dialog(self):
        return None

    def process_config(self, event, params, vars):
        pass
