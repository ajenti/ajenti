import daemon
import logging
import traceback

import aj
import aj.log
from aj.util.pidfile import PidFile


def start(daemonize=False, log_level=logging.INFO, **kwargs):
    """
    A wrapper for :func:`run` that optionally runs it in a forked daemon process.

    :param kwargs: rest of arguments is forwarded to :func:`run`
    """
    # reimport into scope
    import aj

    if daemonize:
        context = daemon.DaemonContext(
            pidfile=PidFile('/var/run/ajenti.pid'),
            detach_process=True,
            files_preserve=range(1024),  # force-closing files breaks gevent badly
        )
        with context:
            aj.log.init_log_directory()
            aj.log.init_log_file()
            import aj.core
            try:
                aj.core.run(**kwargs)
            # pylint: disable=W0703
            except Exception as e:
                handle_crash(e)
    else:
        import aj.core
        try:
            aj.core.run(**kwargs)
        except KeyboardInterrupt:
            pass
        # pylint: disable=W0703
        except Exception as e:
            handle_crash(e)


def handle_crash(exc):
    # todo rework this
    logging.error('Fatal crash occured')
    traceback.print_exc()
    exc.traceback = traceback.format_exc(exc)
    report_path = '/root/%s-crash.txt' % aj.product
    try:
        report = open(report_path, 'w')
    except:
        report_path = './%s-crash.txt' % aj.product
        report = open(report_path, 'w')

    from aj.util import make_report
    report.write(make_report(exc))
    report.close()
    logging.error('Crash report written to %s', report_path)
    # TODO message
    # logging.error('Please submit it to https://github.com/ajenti/ajenti/issues/new')
