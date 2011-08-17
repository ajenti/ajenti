import threading


class ClassProxy (object):
    """
    Wraps class methods into :class:`MethodProxy`, thus making them thread-safe.
    """
    inner = None
    locks = None

    def __init__(self, inner):
        self.inner = inner
        self.locks = {}

    def __getattr__(self, attr):
        if not attr in self.locks:
            self.locks[attr] = threading.Lock()

        return MethodProxy(getattr(self.inner, attr), self.locks[attr])

    def deproxy(self):
        return self.inner


def nonblocking(fun):
    """
    Decorator, prevents a method from being wrapped in a MethodProxy.
    """
    fun.nonblocking = True
    return fun


class MethodProxy (object):
    """
    Prevents a method from being called by two threads simultaneously.
    """
    def __init__(self, method, lock):
        self.lock = lock
        self.method = method

    def __call__(self, *args, **kwargs):
        if hasattr(self.method, 'nonblocking'):
            return self.method(*args, **kwargs)

        self.lock.acquire()

        res = None

        try:
            res = self.method(*args, **kwargs)
        finally:
            self.lock.release()

        return res
