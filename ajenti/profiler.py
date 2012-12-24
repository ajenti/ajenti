import time

_profiles = []
_profiles_running = {}


def profile(name):
    """
    Starts a profiling interval with specific ``name``
    Profiling data is sent to the client with next data batch.
    """
    _profiles_running[name] = time.time()


def profile_end(name):
    """
    Ends a profiling interval with specific ``name``
    """
    _profiles.append((name, time.time() - _profiles_running[name]))


def get_profiles():
    """
    Returns all accumulated profiling values
    """
    global _profiles
    r = []
    r.extend(_profiles)
    _profiles = []
    return r
