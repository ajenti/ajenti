#!/usr/bin/env python
import sys
import getopt
import os.path
import logging

from ajenti.standalone import server

def usage():
    print """
Usage: serve.py [options]
Options:
    -c, --config <file> - Use given config file instead of default
    -v                  - Debug/verbose logging
    -h, --help          - This help   
    """

if __name__ == '__main__':

    log_level = logging.INFO
    config_file = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:v', ['help', 'config='])
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

    server(log_level, config_file)

