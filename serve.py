#!/usr/bin/env python
import sys
import getopt
import os.path
import logging

from ajenti.standalone import server
from ajenti.daemon import Daemon

class AjentiDaemon(Daemon):
	def run(self):
		server(self.log_level, self.config_file)

def usage():
    print """
Usage: %s [method] [options]
Methods:
	start	- Starts Ajenti server
	stop	- Terminates Ajenti
	restart	- Terminate and Start server again
Options:
    -c, --config <file> - Use given config file instead of default
    -v                  - Debug/verbose logging
    -h, --help          - This help   
    """

if __name__ == '__main__':

    log_level = logging.INFO
    config_file = ''
    
    if len(sys.argv) < 2:
		usage()
		sys.exit(2)
		
    method = sys.argv[1]
	
    try:
        opts, args = getopt.getopt(sys.argv[2:], 'hc:v', ['help', 'config='])
    except getopt.GetoptError, e:
        print str(e)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-v',):
            log_level = logging.DEBUG
        elif o in ('-c', '--config'):
            if os.path.isfile(a):
                config_file = a

    # Find default config file
    if not config_file:
        # Check for config file in /etc/ajenti/ajenti.conf
        if os.path.isfile('/etc/ajenti/ajenti.conf'):
            config_file = '/etc/ajenti/ajenti.conf'
        elif os.path.isfile(os.path.join(sys.path[0], 'ajenti.conf')):
            # Try local config file
            config_file = os.path.join(sys.path[0], 'ajenti.conf')

    
    ajentid = AjentiDaemon('./ajenti.pid',stdout='./stdout.log',stderr='./stderr.log')
    ajentid.log_level = log_level
    ajentid.config_file = config_file
	
    if 'start' == sys.argv[1]:
        ajentid.start()
    elif 'stop' == sys.argv[1]:
        ajentid.stop()
    elif 'restart' == sys.argv[1]:
        ajentid.restart()
    else:
        usage()
        sys.exit(2)
		
    sys.exit(0)
