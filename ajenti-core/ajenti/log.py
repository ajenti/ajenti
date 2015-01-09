import logging
import logging.handlers
import os
import sys
import termcolor
from datetime import datetime


LOG_DIR = '/var/log/ajenti'
LOG_NAME = 'ajenti.log'
LOG_FILE = os.path.join(LOG_DIR, LOG_NAME)



class ConsoleHandler (logging.StreamHandler):
    def __init__(self, stream, debug):
        self.debug = debug
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):
        if not self.stream.isatty():
            return logging.StreamHandler.handle(self, record)

        s = ''
        d = datetime.fromtimestamp(record.created)
        s += termcolor.colored(d.strftime("%d.%m.%Y %H:%M  "), 'white') 
        if self.debug:
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
            l = '\033[31mERROR\033[0m '
        s += l + '  ' 


        try:
            s += record.msg % record.args
        except:
            s += record.msg
        s += '\n'
        self.stream.write(s)


def make_log(debug=False, log_level=logging.INFO):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    stdout = ConsoleHandler(sys.stdout, debug)
    stdout.setLevel(log_level)

    dformatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s.%(funcName)s(): %(message)s')
    stdout.setFormatter(dformatter)

    log.addHandler(stdout)


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


def init(level=logging.INFO):
    make_log(debug=level == logging.DEBUG, log_level=level)
