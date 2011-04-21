import threading


class ClassProxy (object):
    inner = None
    locks = None
    
    def __init__(self, inner):
        self.inner = inner
        self.locks = {}

    def __getattr__(self, attr):
        if not attr in self.locks:
            self.locks[attr] = threading.Lock()
            
        return MethodProxy(getattr(self.inner, attr), self.locks[attr])

            
class MethodProxy (object):
    def __init__(self, method, lock):
        self.lock = lock
        self.method = method
        
    def __call__(self, *args, **kwargs):
        self.lock.acquire()
        
        res = None
        
        try:
            res = self.method(*args, **kwargs)
        finally:
            self.lock.release()
            
        return res
