"""
Module for sending usage statistics to ajenti.org
"""

__all__ = ['send_stats', 'check_uid']

import os
import base64
import random

from ajenti.utils import *
from ajenti import version


global uid
uid = ''


def send_stats(server, plugins, addplugin=None, delplugin=None):
    """
    Sends usage statistics to the server. Statistics include: OS name, list of
    installed plugins and Ajenti version.

    :param  server:     server URL
    :type   server:     str
    :param  addplugin:  plugin being currently installed or None
    :type   addplugin:  str
    :param  delplugin:  plugin being currently removed or None
    :type   delplugin:  str
    """
    plugs = []
    plugs.extend(plugins)
    if addplugin:
        plugs.append(addplugin)
    if delplugin and delplugin in plugs:
        plugs.remove(delplugin)
    plugs = ','.join(plugs)
    data = '1|%s|%s|%s|,%s,' % (uid, version(), detect_platform(mapping=False), plugs)
    data = base64.b64encode(data)
    download('http://%s/api/submit?data=%s' % (server, data))


def check_uid():
    """
    Checks that installation UID is present and generates it if it's not.
    """
    global uid
    file = '/var/lib/ajenti/installation-uid'
    if not os.path.exists(file):
        uid = str(random.randint(1, 9000*9000))
        try:
            open(file, 'w').write(uid)
        except:
            uid = '0'
    else:
        uid = open(file).read()
