from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import log
import session
import config

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
		#self.send_header('Content-type', 'text/html')
        self.end_headers()
    	session.process_request(self.client_address[0], self.path, self)


server = None
running = True

def run():
    global server, running
    log.info('HTTP', 'Starting server at http://localhost:%s' % config.http_port)
    server = HTTPServer(('', config.http_port), Handler);
    try:
        server.serve_forever()
    except KeyboardInterrupt, e:
        log.warn('HTTP', 'Stopping by <Control-C>')

