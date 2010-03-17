import re

from ajenti.plugins.core import *
from ajenti.plugins.dashboard import *

from ajenti.com import *
from ajenti.app.api import IRequestDispatcher

class DemoDispatcher(Plugin):
    implements(IRequestDispatcher)

    def match(self, uri):
        if re.match('^/demo',uri):
            return True
        else:
            return False

    def process(self, req, sr):
        return "Demo Page"
 
