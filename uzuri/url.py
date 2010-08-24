from ajenti.com import *
from ajenti.app.urlhandler import URLHandler, url

from api import *


class UzuriHostDispatcher(URLHandler, Plugin):

    @url('^/uzurihost/plugins')
    def process(self, req, start_response):
	p = [x.get_name() for x in self.app.grab_plugins(IClusteredPlugin)]
	s = '\n'.join(p)
        return s
