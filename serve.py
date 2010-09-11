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
Usage: %s [options]
Options:
    -c, --config <file> - Use given config file instead of default
    -v                  - Debug/verbose logging
    -d, --start         - Run in background (daemon mode)
    -r, --restart       - Restart daemon
    -s, --stop          - Stop daemon
    -h, --help          - This help
    """


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    sys.dont_write_bytecode = True

    log_level = logging.INFO
    config_file = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hcdrs:v', ['help', 'config=', 'start', 'stop', 'restart'])
    except getopt.GetoptError, e:
        print str(e)
        usage()
        sys.exit(2)

    action = 'run'

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-v',):
            log_level = logging.DEBUG
        elif o in ('-c', '--config'):
            if os.path.isfile(a):
                config_file = a
        elif o in ('-d', '--start'):
            action = 'start'
        elif o in ('-r', '--restart'):
            action = 'restart'
        elif o in ('-s', '--stop'):
            action = 'stop'

    # Find default config file
    if not config_file:
        # Check for config file in /etc/ajenti/ajenti.conf
        if os.path.isfile('/etc/ajenti/ajenti.conf'):
            config_file = '/etc/ajenti/ajenti.conf'
        elif os.path.isfile(os.path.join(sys.path[0], 'ajenti.conf')):
            # Try local config file
            config_file = os.path.join(sys.path[0], 'ajenti.conf')

    if action == 'run':
        server(log_level, config_file)
    else:
        ajentid = AjentiDaemon('/var/run/ajenti.pid',stdout='/var/log/ajenti.log',stderr='/var/log/ajenti.err.log')
        ajentid.log_level = log_level
        ajentid.config_file = config_file

        if 'start' == action:
            ajentid.start()
        elif 'stop' == action:
            ajentid.stop()
        elif 'restart' == action:
            ajentid.restart()
        else:
            usage()
            sys.exit(2)

    sys.exit(0)
