# Global state

config = None
version = None

""" Current platform """
platform = None

""" Current platform without Ubuntu=Debian mapping """
platform_unmapped = None

""" Human-friendly platform name """
platform_string = None

""" Unique installation ID """
installation_uid = None

""" Web server """
server = None

""" Debug mode """
debug = False


__all__ = [platform, platform_string, platform_unmapped, installation_uid, version, server, debug, 'init']


import build
import subprocess
import os
import platform
import random


def detect_version():
    p = subprocess.Popen('git describe --tags 2> /dev/null',
            shell=True,
            stdout=subprocess.PIPE)
    if p.wait() != 0:
        return build.version
    return p.stdout.read().strip('\n ')


def detect_platform():
    base_mapping = {
        'gentoo base system': 'gentoo',
        'centos linux': 'centos',
        'mandriva linux': 'mandriva',
    }

    platform_mapping = {
        'ubuntu': 'debian',
        'linuxmint': 'debian',
        'elementary os': 'debian',
    }

    if platform.system() != 'Linux':
        return platform.system().lower()

    dist = ''
    (maj, min, patch) = platform.python_version_tuple()
    if (maj * 10 + min) >= 26:
        dist = platform.linux_distribution()[0]
    else:
        dist = platform.dist()[0]

    if dist == '':
        try:
            dist = subprocess.check_output(['strings', '-4', '/etc/issue']).split()[0]
        except:
            dist = 'unknown'

    res = dist.strip(' \'"\t\n\r').lower()
    if res in base_mapping:
        res = base_mapping[res]

    res_mapped = res
    if res in platform_mapping:
        res_mapped = platform_mapping[res]
    return res, res_mapped


def detect_platform_string():
    try:
        return subprocess.check_output(['lsb_release',  '-sd'])
    except:
        return subprocess.check_output(['uname', '-mrs'])


def check_uid():
    file = '/var/lib/ajenti/installation-uid'
    if not os.path.exists(file):
        uid = str(random.randint(1, 9000 * 9000))
        try:
            open(file, 'w').write(uid)
        except:
            uid = '0'
    else:
        uid = open(file).read()
    return uid


def init():
    import ajenti
    ajenti.version = detect_version()
    ajenti.platform_unmapped, ajenti.platform = detect_platform()
    ajenti.platform_string = detect_platform_string()
    ajenti.installation_uid = check_uid()
