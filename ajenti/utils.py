import commands
import platform

def detect_platform():
    if platform.system() != 'Linux':
        return platform.system().lower()

    dist = ''
    (maj, min, patch) = platform.python_version_tuple()
    if (maj * 10 + min) >= 26:
        dist = platform.linux_distribution()[0]
    else:
        dist = platform.dist()[0]

    if dist == '':
        dist='unknown'

    return dist

def detect_distro():
    s, r = commands.getstatusoutput('lsb_release -sd')
    if s == 0: return r
    s, r = commands.getstatusoutput('uname -mrs')
    return r

def shell(c):
    return commands.getstatusoutput(c)[1]
