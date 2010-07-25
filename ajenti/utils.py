import subprocess
import platform

def dequote(s):
    s = str(s).replace('[br]', '\n').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    return s

def fix_unicode(s):
    return s.encode('utf-8', 'xmlcharref')
    
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

    return dist.strip()

def detect_distro():
    if shell_status('lsb_release -sd') == 0:
        return shell('lsb_release -sd')
    return shell('uname -mrs')

def shell(c):
    p = subprocess.Popen(c, shell=True, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    p.wait()
    return p.stdout.read() + p.stderr.read()

def shell_status(c):
    return subprocess.Popen(c, shell=True).wait()
    
