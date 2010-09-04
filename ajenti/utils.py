import subprocess
import platform
import os
import mimetypes
from datetime import datetime


def dequote(s):
    s = str(s).replace('[br]', '\n').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    return s

def enquote(s):
    s = s.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
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
        try:
            dist = open('/etc/issue').read().strip('\n\t ').split()[0]
        except:
            dist = 'unknown'

    return dist.strip()

def detect_distro():
    if shell_status('lsb_release -sd') == 0:
        return shell('lsb_release -sd')
    return shell('uname -mrs')

def shell(c):
    p = subprocess.Popen(c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)

    data = p.stdout.read() # Workaround; waiting first causes a deadlock
    p.wait()
    return data + p.stdout.read() + p.stderr.read()

def shell_status(c):
    return subprocess.Popen(c, shell=True).wait()

def shell_stdin(c, input):
    p = subprocess.Popen(c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)
    return p.communicate(input)

def wsgi_serve_file(req, start_response, file):
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
            self.log.debug('Asked for If-Modified-Since: %s'%rtime)
            rtime = datetime.strptime(rtime, '%a, %b %d %Y %H:%M:%S GMT')
            if mtime <= rtime:
                start_response('304 Not Modified',[])
                return ''
        except:
            pass

    headers.append(('Content-length',str(size)))
    headers.append(('Last-modified',mtime.strftime('%a, %b %d %Y %H:%M:%S GMT')))
    start_response('200 OK', headers)
    return req['wsgi.file_wrapper'](open(file))
