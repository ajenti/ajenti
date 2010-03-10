from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import log
import session

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
    	#log.info('HTTP', 'Request from ' + self.client_address[0])
        self.send_response(200, 'OK')
#        self.send_header('Content-type', 'text/html')
        self.end_headers()
    	session.ProcessRequest(self.client_address[0], self.path, self)


Server = None
Running = True

def Run():
	global Server, Running
	log.info('HTTP', 'Starting server')
	Server = HTTPServer(('', 8000), Handler);
	Server.serve_forever()
