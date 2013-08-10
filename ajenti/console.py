import sys
import signal
import logging
import traceback
from ajenti.util import public

@public
def register():
    logging.info('Debug mode: press Ctrl-\\ to enter interactive console')
    signal.signal(signal.SIGQUIT, handle_quit)
    sys.excepthook = handle_exception


def handle_exception(type, value, tb):
    print 'FATAL CRASH'
    print value
    print '\n'.join(traceback.format_tb(tb))
    launch()


def handle_quit(*args):
    print '\nSIGQUIT received at:'
    traceback.print_stack()
    launch()


@public
def launch(*args):
    print '\nActivating emergency console\n'

    import readline
    import code
    import ajenti
    from ajenti.plugins import manager

    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)

    print 'Press Ctrl-D to exit console'
    print 'Plugin manager is available as \'manager\'\n'
    shell.interact()
