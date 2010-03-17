import re
import os.path
import mimetypes

from ajenti.com import *
from ajenti.app.api import IRequestDispatcher

class Downloader(Plugin):
    implements(IRequestDispatcher)

    def match(self, uri):
        if re.match('^/dl/.+/.+', uri):
            return True
        else:
            return False

    def process(self, req, start_response):
        params = req['PATH_INFO'].split('/',3)

        # Check if we have module in content path
        if params[2] not in self.app.content:
            start_response('404 Not Found',[])
            return ''

        path = self.app.content[params[2]]
        file = os.path.join(path, params[3])
        # Check if this is a file
        if not os.path.isfile(file):
            start_response('404 Not Found',[])
            return ''

        headers = []
        # Check if we have any known file type 
        (mimetype, encoding) = mimetypes.guess_type(file)
        if mimetype is not None:
            headers.append(('Content-type',mimetype))

        size = os.path.getsize(file)
        headers.append(('Content-length',str(size)))

        start_response('200 OK', headers)
        return open(file).read()

