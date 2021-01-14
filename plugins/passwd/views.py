"""
Handle user and passwords stored in /etc/shadow.
"""

import pwd
import subprocess

from jadi import component
from aj.api.http import url, HttpPlugin

from aj.api.endpoint import endpoint


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/passwd/list')
    @endpoint(api=True)
    def handle_api_passwd_list(self, http_context):
        """
        Provide a dict of user from the /etc/shadow file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of user, one per dict
        :rtype:list of dict
        """

        return [
            {
                'uid': x.pw_uid,
                'gid': x.pw_gid,
                'name': x.pw_name,
                'gecos': x.pw_gecos,
                'home': x.pw_dir,
                'shell': x.pw_shell,
            }
            for x in pwd.getpwall()
        ]

    @url(r'/api/passwd/set')
    @endpoint(api=True)
    def handle_api_passwd_set(self, http_context):
        """
        Set new password for the selected user.
        Method POST.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        data = http_context.json_body()
        p = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE)
        p.communicate('%s:%s' % (data['user'], data['password']))
