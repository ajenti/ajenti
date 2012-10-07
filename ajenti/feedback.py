"""
Module for sending usage statistics to ajenti.org
"""


import base64

import ajenti


def send_stats(server, plugins):
    """
    Sends usage statistics to the server. Statistics include: OS name, list of
    installed plugins and Ajenti version.

    :param  server:  server URL
    :type   server:  str
    """
    plugins = ','.join(plugins)
    data = '1|%s|%s|%s|,%s,' % (ajenti.installation_uid, ajenti.version, ajenti.platform, plugins)
    data = base64.b64encode(data)
    #download('http://%s/api/submit?data=%s' % (server, data))

__all__ = ['send_stats']
