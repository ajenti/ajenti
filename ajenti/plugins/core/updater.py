from ajenti.api import *
from ajenti import plugmgr

import time
import feedparser


FEED_URL = 'http://ajenti.org/?cat=4&feed=atom'


class Updater (Component):
    name = 'updater'

    def on_starting(self):
        self.feed = None

    def get_feed(self): return self.feed

    def run(self):
        pm = plugmgr.PluginManager(self.app.config)

        while True:
            try:
                pm.update_list()
                self.feed = feedparser.parse(FEED_URL)
            except:
                pass
            time.sleep(60*60*12) # each 12 hrs
