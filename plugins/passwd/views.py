import pwd

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
