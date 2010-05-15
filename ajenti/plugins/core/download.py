import os.path
import mimetypes
from datetime import datetime

from ajenti.com import *
from ajenti.app.urlhandler import URLHandler, url

class Downloader(URLHandler, Plugin):

    @url('^/dl/.+/.+')
    def process(self, req, start_response):
        params = req['PATH_INFO'].split('/',3)
        self.log.debug('Dispatching download: %s'%req['PATH_INFO'])

        # Check if we have module in content path
        if params[2] not in self.app.content:
            start_response('404 Not Found',[])
            return ''

        path = self.app.content[params[2]]
        file = os.path.join(path, params[3])

        return self.serve_file(req, start_response, path, file)

    @url('^/static/.+')
    def process(self, req, start_response):
        params = req['PATH_INFO'].split('/',2)
        self.log.debug('Dispatching static: %s'%req['PATH_INFO'])

        path = self.config.get('ajenti','static')
        file = os.path.join(path, params[2])

        return self.serve_file(req, start_response, path, file)

    def serve_file(self, req, start_response, path, file):
        # Check for directory traversal
        if file.find('..') > -1:
            start_response('404 Not Found',[])
            return ''
             
        # Check if this is a file
        if not os.path.isfile(file):
            start_response('404 Not Found',[])
            return ''

        headers = []
        # Check if we have any known file type
        # For faster response, check for known types:
        content_type = 'application/octet-stream'
        if file.endswith('.css'):
            content_type = 'text/css'
        elif file.endswith('.js'):
            content_type = 'application/javascript'
        elif file.endswith('.png'):
            content_type = 'image/png'
        else:
            (mimetype, encoding) = mimetypes.guess_type(file)
            if mimetype is not None:
                content_type = mimetype
        headers.append(('Content-type',content_type))

        size = os.path.getsize(file)
        mtimestamp = os.path.getmtime(file)
        mtime = datetime.utcfromtimestamp(mtimestamp)

        rtime = req.get('HTTP_IF_MODIFIED_SINCE', None)
        if rtime is not None:
            try:
                self.log.debug('Asked for If-Modified-Since: %s'%rtime)
                rtime = datetime.strptime(rtime, '%a, %b %d %Y %H:%M:%S GMT')
                if mtime <= rtime:
                    start_response('304 Not Modified',[])
                    return ''
            except:
                pass 

        headers.append(('Content-length',str(size)))
        headers.append(('Last-modified',mtime.strftime('%a, %b %d %Y %H:%M:%S GMT')))

        start_response('200 OK', headers)

        self.log.debug('Finishing download: %s'%req['PATH_INFO'])
        return req['wsgi.file_wrapper'](open(file))

