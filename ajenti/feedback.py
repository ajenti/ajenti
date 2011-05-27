import os
import base64
import random

import ajenti.plugmgr
from ajenti.utils import *
from ajenti import version


global uid
uid = ''


def send_stats(server, addplugin=None, delplugin=None):
    plugs = []
    plugs.extend(ajenti.plugmgr.loaded_plugins)
    if addplugin:
        plugs.append(addplugin)
    if delplugin and delplugin in plugs:
        plugs.remove(delplugin)
    plugs = ','.join(plugs)
    data = '1|%s|%s|%s|,%s,' % (uid, version(), detect_platform(mapping=False), plugs)
    data = base64.b64encode(data)
    download('http://%s/api/submit?data=%s' % (server, data))
    
def check_uid():
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
    
