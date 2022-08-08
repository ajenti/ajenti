from gevent import pywsgi, spawn

def http_to_https(target_url):

    def app(environ, start_response):

        if environ['PATH_INFO'] == "/":
            start_response(
                            '301 Move Permanently',
                            [
                                ('Location', target_url),
                                ('Connection', 'close'),
                                ('Cache-control', 'private')
                            ])
            return [b"""
    <html>
    <body>
        Migrating to HTTPS protocol.
        Please go to <a href='{self.target}'>{self.target}</a> to use Ajenti.
    </body>
    </html>"""]
        start_response('404 Not Found', [('Content-Type', 'text/html')])

        return [b'<h1>Not Found</h1>']

    pywsgi.WSGIServer(
        ('', 80),
        application = app,
    ).serve_forever()
