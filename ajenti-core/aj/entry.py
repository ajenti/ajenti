import daemon
import logging
import traceback
from datetime import datetime

from aj.util.pidfile import PidFile


def start(daemonize=False, log_level=logging.INFO, dev_mode=False, **kwargs):
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
            files_preserve=list(range(1024)),  # force-closing files breaks gevent badly
        )
        with context:
            aj.log.init_log_directory()
            aj.log.init_log_file(log_level)
            import aj.core
            try:
                aj.core.run(dev_mode=dev_mode, **kwargs)
            # pylint: disable=W0703
            except Exception as e:
                handle_crash(e)
    else:
        if not dev_mode:
            aj.log.init_log_directory()
            aj.log.init_log_file(log_level)
        import aj.core
        try:
            aj.core.run(dev_mode=dev_mode, **kwargs)
        except KeyboardInterrupt:
            pass
        # pylint: disable=W0703
        except Exception as e:
            handle_crash(e)


def handle_crash(exc):
    # todo rework this
    now = datetime.now().strftime('%Y-%m-%d-%Hh%M')
    logging.error('Fatal crash occured')
    traceback.print_exc()
    exc.traceback = traceback.format_exc()
    report_path = f'/var/log/ajenti/crash-{now}.txt'
    try:
        report = open(report_path, 'w')
    except Exception as e:
        report_path = f'./crash-{now}.txt'
        report = open(report_path, 'w')

    from aj.util import make_report
    report.write(make_report(exc))
    report.close()
    logging.error(f'Crash report written to {report_path}')
    logging.error('Please submit it to https://github.com/ajenti/ajenti/issues/new')
