import gevent
import subprocess


def subprocess_call_background(*args, **kwargs):
    p = subprocess.Popen(*args, **kwargs)
    gevent.sleep(0)
    return p.wait()


def subprocess_check_output_background(*args, **kwargs):
    p = subprocess.Popen(*args, stdout=subprocess.PIPE, **kwargs)
    gevent.sleep(0)
    return p.communicate()[0]
