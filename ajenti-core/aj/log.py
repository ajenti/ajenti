import logging
import logging.handlers
import os
import sys
from termcolor import colored
from datetime import datetime

import aj

LOG_DIR = '/var/log/ajenti'
LOG_NAME = 'ajenti.log'
LOG_FILE = os.path.join(LOG_DIR, LOG_NAME)
LOG_PARAMS = {
    'master_pid': None,
    'tag': 'master',
}


class ConsoleHandler (logging.StreamHandler):
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):
        if not self.stream.isatty():
            return logging.StreamHandler.handle(self, record)

        s = ''
        d = datetime.fromtimestamp(record.created)
        s += colored(d.strftime("%d.%m.%Y %H:%M  "), 'white')

        process_tag = ''
        padding = ''
        if LOG_PARAMS['tag'] == 'master':
            if os.getpid() == LOG_PARAMS['master_pid']:
                process_tag = colored('master', 'yellow')
            else:
                LOG_PARAMS['tag'] = 'worker'
                #process_tag = colored('...   ', 'yellow')
        if LOG_PARAMS['tag'] == 'worker':
            process_tag = colored('worker', 'green')
            padding = '  '
        if LOG_PARAMS['tag'] == 'task':
            process_tag = colored('task  ', 'blue')
            padding = '    '
        s += colored('[', 'white')
        s += process_tag
        s += colored(' %5i]  ' % os.getpid(), 'white')

        if aj.debug:
            s += colored(('%15s:%-4s  ' % (record.filename[-15:], record.lineno)), 'grey', attrs=['bold'])

        l = ''
        if record.levelname == 'DEBUG':
            l = colored('DEBUG', 'white')
        if record.levelname == 'INFO':
            l = colored('INFO ', 'green', attrs=['bold'])
        if record.levelname == 'WARNING':
            l = colored('WARN ', 'yellow', attrs=['bold'])
        if record.levelname == 'ERROR':
            l = colored('ERROR', 'red', attrs=['bold'])
        s += l + '  '

        s += padding

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


def set_log_params(**kwargs):
    LOG_PARAMS.update(kwargs)
