import subprocess
import platform
import os
import mimetypes
import time
import urllib
from datetime import datetime
from hashlib import sha1
from base64 import b64encode


import ajenti.utils 


def enquote(s):
    s = s.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
    return s

def fix_unicode(s):
    d = ''.join(max(i, ' ') if not i in ['\n', '\t', '\r'] else i for i in s)
    return unicode(d.encode('utf-8', 'xmlcharref'), errors='replace')

def detect_platform(mapping=True):
    platform_mapping = {
        'ubuntu': 'debian',
        'linuxmint': 'debian'
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
    if mapping:
        if res in platform_mapping:
            res = platform_mapping[res]
    return res

def detect_distro():
    if shell_status('lsb_release -sd') == 0:
        return shell('lsb_release -sd')
    return shell('uname -mrs')

def download(url, file=None, crit=False):
    try:
        # ajenti.utils.logger.debug('Downloading %s' % url)
        if file:
            urllib.urlretrieve(url, file)
        else:
            return urllib.urlopen(url).read()
    except Exception, e:
        # ajenti.utils.logger.debug('Download failed')
        if crit:
            raise
        
def shell(c):
    #ajenti.utils.logger.debug('Running %s' % c)
    p = subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    
    try:
        data = p.stdout.read() # Workaround; waiting first causes a deadlock
    except: # WTF OSError (interrupted request)
        data = ''
    p.wait()
    return data + p.stdout.read() + p.stderr.read()

def shell_bg(c, output=None, deleteout=False):
    if output is not None:
        c = 'LC_ALL=C bash -c "%s" > %s 2>&1'%(c,output)
        if deleteout:
            c = 'touch %s; %s; rm -f %s'%(output,c,output)
    #ajenti.utils.logger.debug('Running in background: %s' % c)
    subprocess.Popen(c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
    
def shell_status(c):
    #ajenti.utils.logger.debug('Running %s' % c)
    return subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE).wait()

def shell_stdin(c, input):
    #ajenti.utils.logger.debug('Running %s' % c)
    p = subprocess.Popen('LC_ALL=C '+c, shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE)
    return p.communicate(input)


def hashpw(passw):
    return '{SHA}' + b64encode(sha1(passw).digest())
        
def str_fsize(sz):
    if sz < 1024:
        return '%i bytes' % sz
    sz /= 1024
    if sz < 1024:
        return '%i Kb' % sz
    sz /= 1024
    if sz < 1024:
        return '%i Mb' % sz
    sz /= 1024
    return '%i Gb' % sz

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
    return open(file).read()
