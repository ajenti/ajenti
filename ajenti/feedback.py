"""
Module for sending usage statistics to ajenti.org
"""

__all__ = ['send_stats', 'check_uid']

import os
import base64
import random

import ajenti


def send_stats(server, plugins):
    """
    Sends usage statistics to the server. Statistics include: OS name, list of
    installed plugins and Ajenti version.

    :param  server:     server URL
    :type   server:     str
    """
    plugins = ','.join(plugins)
    data = '1|%s|%s|%s|,%s,' % (ajenti.installation_uid, ajenti.version, ajenti.platform, plugs)
    data = base64.b64encode(data)
    download('http://%s/api/submit?data=%s' % (server, data))


