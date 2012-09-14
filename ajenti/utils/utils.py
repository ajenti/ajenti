import subprocess
import platform
import os
import mimetypes
import urllib
from datetime import datetime
from hashlib import sha1
from base64 import b64encode
from passlib.hash import sha512_crypt


def enquote(s):
    """
    Inserts ``&lt;`` and ``&gt;`` entities and replaces newlines with ``<br/>``.
    """
    s = s.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
    return s

def fix_unicode(s):
    """
    Tries to fix a broken Unicode string.

    :rtype: str
    """
    d = ''.join(max(i, ' ') if not i in ['\n', '\t', '\r'] else i for i in s)
    return unicode(d.encode('utf-8', 'xmlcharref'), errors='replace')

def detect_platform(mapping=True):
    """
    Returns a text shortname of the current system platform.

    :param  mapping:    if True, map Ubuntu to Debian and so on.
    :type   mapping:    bool
    :rtype:             str
    """
    base_mapping = {
        'gentoo base system': 'gentoo',
        'centos linux': 'centos',
        'mandriva linux': 'mandriva',
    }

    platform_mapping = {
        'ubuntu': 'debian',
        'linuxmint': 'debian',
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
            dist = shell('strings -4 /etc/issue').split()[0]
        except:
            dist = 'unknown'

    res = dist.strip().lower()
    if res in base_mapping:
        res = base_mapping[res]
    if mapping:
        if res in platform_mapping:
            res = platform_mapping[res]
    return res

def detect_distro():
    """
    Returns human-friendly OS name.
    """
    if shell_status('lsb_release -sd') == 0:
        return shell('lsb_release -sd')
    return shell('uname -mrs')

def download(url, file=None, crit=False):
    """
    Downloads data from an URL

    :param  file:   file path to save data into. If None, returns data as string
    :param  crit:   if False, exceptions will be swallowed
    :rtype:         None or str
    """
    try:
        data = urllib.urlopen(url).read()
        if file:
            open(file, 'w').write(data)
        else:
            return data
    except Exception, e:
        if crit:
            raise

def shell(c, stderr=False):
    """
    Runs commandline in the default shell and returns output. Blocking.
    """
    p = subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)

    try:
        data = p.stdout.read() # Workaround; waiting first causes a deadlock
    except: # WTF OSError (interrupted request)
        data = ''
    p.wait()
    return data + p.stdout.read() + (p.stderr.read() if stderr else '')

def shell_bg(c, output=None, deleteout=False):
    """
    Same, but runs in background. For controlled execution, see
    :class:BackgroundProcess.

    :param  output:     if not None, saves output in this file
    :type   output:     str
    :param  deleteout:  if True, will delete output file upon completion
    :type   deleteout:  bool
    """
    if output is not None:
        c = 'LC_ALL=C bash -c "%s" > %s 2>&1'%(c,output)
        if deleteout:
            c = 'touch %s; %s; rm -f %s'%(output,c,output)
    subprocess.Popen(c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)

def shell_status(c):
    """
    Same, but returns the exitcode.
    """
    return subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE).wait()

def shell_stdin(c, input):
    """
    Same, but feeds input to process' stdin and returns its stdout
    upon completion.
    """
    p = subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)
    return p.communicate(input)


def hashpw(passw, scheme = 'sha512_crypt'):
    """
    Returns a hashed form of given password. Default scheme is
    sha512_crypt.
    """
    if scheme == 'sha512_crypt':
        return sha512_crypt.encrypt(passw)
    elif scheme == 'sha':
        return '{SHA}' + b64encode(sha1(passw).digest())
    return sha512_crypt.encrypt(passw)

def str_fsize(sz):
    """
    Formats file size as string (1.2 Mb)
    """
    if sz < 1024:
        return '%.1f bytes' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f Kb' % sz
    sz /= 1024.0
    if sz < 1024:
        return '%.1f Mb' % sz
    sz /= 1024.0
    return '%.1f Gb' % sz

def wsgi_serve_file(req, start_response, file):
    """
    Serves a file as WSGI reponse.
    """
    # Check for directory traversal
    if file.find('..') > -1:
        start_response('404 Not Found', [])
        return ''

    # Check if this is a file
    if not os.path.isfile(file):
        start_response('404 Not Found',[])
        return ''

    headers = []
    # Check if we have any known file type
    # For faster response, check for known types:
    content_type = 'application/octet-stream'
    if file.endswith('.css'):
        content_type = 'text/css'
    elif file.endswith('.less'):
        content_type = 'text/css'
    elif file.endswith('.js'):
        content_type = 'application/javascript'
    elif file.endswith('.png'):
        content_type = 'image/png'
    else:
        (mimetype, encoding) = mimetypes.guess_type(file)
        if mimetype is not None:
            content_type = mimetype
    headers.append(('Content-type',content_type))

    size = os.path.getsize(file)
    mtimestamp = os.path.getmtime(file)
    mtime = datetime.utcfromtimestamp(mtimestamp)

    rtime = req.get('HTTP_IF_MODIFIED_SINCE', None)
    if rtime is not None:
        try:
            rtime = datetime.strptime(rtime, '%a, %b %d %Y %H:%M:%S GMT')
            if mtime <= rtime:
                start_response('304 Not Modified',[])
                return ''
        except:
            pass

    headers.append(('Content-length',str(size)))
    headers.append(('Last-modified',mtime.strftime('%a, %b %d %Y %H:%M:%S GMT')))
    start_response('200 OK', headers)
    return open(file).read()
