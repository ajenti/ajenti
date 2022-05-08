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


class ConsoleHandler(logging.StreamHandler):
    def __init__(self, stream):
        logging.StreamHandler.__init__(self, stream)

    def handle(self, record):
        if not self.stream.isatty():
            return logging.StreamHandler.handle(self, record)

        s = ''
        d = datetime.fromtimestamp(record.created)
        s += colored(d.strftime("%d.%m.%Y %H:%M:%S  "), 'white')

        params = {
            'tag': getattr(record, 'tag', 'master'),
            'pid': getattr(record, 'pid', os.getpid()),
        }

        process_tag = ''
        padding = ''
        if params['tag'] == 'master':
            if os.getpid() == LOG_PARAMS['master_pid']:
                process_tag = colored('master', 'yellow')
            else:
                params['tag'] = None
        if params['tag'] == 'restricted':
            process_tag = colored('rstrct', 'red')
            padding = '  '
        if params['tag'] == 'worker':
            process_tag = colored('worker', 'green')
            padding = '  '
        if params['tag'] == 'task':
            process_tag = colored('task  ', 'blue')
            padding = '    '
        if params['tag'] is None:
            process_tag = colored('...   ', 'blue')
            padding = '  '
        s += colored('[', 'white')
        s += process_tag
        s += colored(' %5i]  ' % params['pid'], 'white')

        if aj.debug:
            s += colored(
                ('%15s:%-4s  ' % (record.filename[-15:], record.lineno)),
                'magenta',
                attrs=['bold']
            )

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
        except TypeError:
            # Not enough arguments can be caused by encoded URL
            s += record.msg
        s += '\n'
        self.stream.write(s)


def init_console(log_level=logging.INFO):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    stdout = ConsoleHandler(sys.stdout)
    stdout.setLevel(log_level)
    log.handlers = [stdout]


class LoggerWriter:
    def write(self, message):
        if message != '\n':
            message = message.strip("\n")
            logging.warning(f'stdout: {message}')

    def flush(self):
        pass


def init_log_directory():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    os.chmod(LOG_DIR, 0o640)


def init_log_file(log_level=logging.INFO):
    #sys.stderr = sys.stdout = LoggerWriter()
    if not os.path.isfile(LOG_FILE):
        os.mknod(LOG_FILE)
    os.chmod(LOG_FILE, 0o640)
    log = logging.getLogger()
    try:
        handler = logging.handlers.TimedRotatingFileHandler(
            LOG_FILE,
            when='midnight',
            backupCount=7
        )
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s'))
        log.handlers = [handler]
    except IOError:
        pass

    return log


def init_log_forwarding(fx):
    methods = ['info', 'warn', 'debug', 'error', 'critical']
    for method in methods:
        setattr(
            logging,
            method,
            (lambda method: lambda message, *args: fx(
                method,
                message,
                tag=LOG_PARAMS['tag'],
                pid=os.getpid(),
                *args
            ))(method)
        )


def set_log_params(**kwargs):
    LOG_PARAMS.update(kwargs)
