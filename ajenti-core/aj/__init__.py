import logging
import os
import platform as pyplatform
import signal
import subprocess

__version__ = '2.2.1'

# Global state

product = None
""" Custom product name """

config = None
""" Configuration dict"""

users = None
""" Users list for auth plugin """

version = None
""" Ajenti version """

platform = None
""" Current platform """

platform_unmapped = None
""" Current platform without "Ubuntu is Debian"-like mapping """

platform_string = None
""" Human-friendly platform name """

server = None
""" Web server """

debug = False
""" Debug mode """

dev = False
""" Dev mode """

context = None

edition = 'vanilla'

master = True

plugin_providers = []

sessions = {}

python_version = None


__all__ = [
    'config', 'platform', 'platform_string', 'platform_unmapped',
    'version', 'server', 'debug', 'init',
    'exit', 'restart', 'python_version'
]


def detect_version():
    return __version__
    ## No git tag yet for ajenti 2
    # p = subprocess.Popen(
        # 'git describe --tags 2> /dev/null',
        # shell=True,
        # stdout=subprocess.PIPE
    # )
    # if p.wait() != 0:
        # return __version__
    # return p.stdout.read().strip(b'\n ').decode()


def detect_python():
    return pyplatform.python_version()

def detect_platform():
    base_mapping = {
        'gentoo base system': 'gentoo',
        'centos linux': 'centos',
        'mandriva linux': 'mandriva',
        'elementary os': 'ubuntu',
        'trisquel': 'ubuntu',
        'linaro': 'ubuntu',
        'linuxmint': 'ubuntu',
        'amazon': 'ubuntu',
        'redhat enterprise linux': 'rhel',
        'red hat enterprise linux server': 'rhel',
        'oracle linux server': 'rhel',
        'fedora': 'rhel',
        'olpc': 'rhel',
        'xo-system': 'rhel',
        'kali linux': 'debian',
    }

    platform_mapping = {
        'ubuntu': 'debian',
        'rhel': 'centos',
    }

    if hasattr(pyplatform, 'mac_ver') and pyplatform.mac_ver()[0] != '':
        return 'osx', 'osx'

    if pyplatform.system() != 'Linux':
        res = pyplatform.system().lower()
        return res, res

    dist = ''
    (major, minor, _) = pyplatform.python_version_tuple()
    major = int(major)
    minor = int(minor)
    if (major * 10 + minor) >= 36:
        import distro
        dist = distro.linux_distribution()[0].split()[0]
    elif (major * 10 + minor) >= 26:
        dist = pyplatform.linux_distribution()[0]
    else:
        dist = pyplatform.dist()[0]

    if dist == '':
        if os.path.exists('/etc/os-release'):
            release = open('/etc/os-release').read()
            if 'Arch Linux' in release:
                dist = 'arch'

    if dist == '':
        if os.path.exists('/etc/system-release'):
            release = open('/etc/system-release').read()
            if 'Amazon Linux AMI' in release:
                dist = 'centos'

    if dist == '':
        try:
            dist = subprocess.check_output(['strings', '-4', '/etc/issue']).split()[0].strip().decode()
        except subprocess.CalledProcessError as e:
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
        return subprocess.check_output(['lsb_release', '-sd']).strip().decode()
    except subprocess.CalledProcessError as e:
        return subprocess.check_output(['uname', '-mrs']).strip().decode()
    except FileNotFoundError:
        logging.warning('Please install lsb_release to detect the platform!')
        return subprocess.check_output(['uname', '-mrs']).strip().decode()


def init():
    import aj
    aj.version = detect_version()
    if aj.platform is None:
        aj.platform_unmapped, aj.platform = detect_platform()
    else:
        logging.warning('Platform ID was enforced by commandline!')
        aj.platform_unmapped = aj.platform
    aj.platform_string = detect_platform_string()
    aj.python_version = detect_python()

# skipcq: PYL-W0622
def exit():
    os.kill(os.getpid(), signal.SIGQUIT)


def restart():
    server.restart_marker = True
    server.stop()
