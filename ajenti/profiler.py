import time

_profiles = {}
_profiles_running = {}
_profiles_stack = []


def profile_start(name):
    """
    Starts a profiling interval with specific ``name``
    Profiling data is sent to the client with next data batch.
    """
    _profiles_running[name] = time.time()
    _profiles_stack.append(name)


def profile_end(name=None):
    """
    Ends a profiling interval with specific ``name``
    """
    last_name = _profiles_stack.pop()
    name = name or last_name
    if not name in _profiles:
        _profiles[name] = 0.0
    _profiles[name] += time.time() - _profiles_running[name]


def get_profiles():
    """
    Returns all accumulated profiling values
    """
    global _profiles
    r = _profiles
    _profiles = {}
    return r


def profiled(namefx=None):
    def decorator(fx):
        def wrapper(*args, **kwargs):
            if namefx:
                profile_start(namefx(args, kwargs))
            else:
                profile_start('%s %s %s' % (fx.__name__, args, kwargs))
            r = fx(*args, **kwargs)
            profile_end()
            return r

        return wrapper
    return decorator
