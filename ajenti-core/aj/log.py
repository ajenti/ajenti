import logging
import logging.handlers
import os
import sys
import termcolor
from datetime import datetime

import aj

LOG_DIR = '/var/log/ajenti'
LOG_NAME = 'ajenti.log'
LOG_FILE = os.path.join(LOG_DIR, LOG_NAME)



class ConsoleHandler (logging.StreamHandler):
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):
        if not self.stream.isatty():
            return logging.StreamHandler.handle(self, record)

        s = ''
        d = datetime.fromtimestamp(record.created)
        s += termcolor.colored(d.strftime("%d.%m.%Y %H:%M  "), 'white') 
        if aj.debug:
            s += termcolor.colored(('%s:%s' % (record.filename, record.lineno)), 'grey', attrs=['bold']).ljust(35)

        s += termcolor.colored('[%5i]  ' % os.getpid(), 'white')
        
        l = ''
        if record.levelname == 'DEBUG':
            l = termcolor.colored('DEBUG', 'white')
        if record.levelname == 'INFO':
            l = termcolor.colored('INFO ', 'green', attrs=['bold'])
        if record.levelname == 'WARNING':
            l = termcolor.colored('WARN ', 'yellow', attrs=['bold'])
        if record.levelname == 'ERROR':
            l = termcolor.colored('ERROR', 'red', attrs=['bold'])
        s += l + '  ' 


        try:
            s += record.msg % record.args
        except:
            s += record.msg
        s += '\n'
        self.stream.write(s)


def init_console(log_level=logging.INFO):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    stdout = ConsoleHandler(sys.stdout)
    stdout.setLevel(log_level)

    dformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s.%(funcName)s(): %(message)s')
    stdout.setFormatter(dformatter)
    log.handlers = [stdout]


def init_log_directory():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)


def init_log_rotation():
    log = logging.getLogger()
    try:
        handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(LOG_DIR, LOG_NAME),
            when='midnight',
            backupCount=7
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s'))
        log.addHandler(handler)
    except IOError:
        pass

    return log
