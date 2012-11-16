import time

_profiles = []
_profiles_running = {}


def profile(name):
    _profiles_running[name] = time.time()


def profile_end(name):
    _profiles.append((name, time.time() - _profiles_running[name]))


def get_profiles():
    global _profiles
    r = []
    r.extend(_profiles)
    _profiles = []
    return r
