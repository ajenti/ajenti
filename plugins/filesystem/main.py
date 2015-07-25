from jadi import component

from aj.auth import PermissionProvider


@component(PermissionProvider)
class Permissions (PermissionProvider):
    def provide(self):
        return [
            {
                'id': 'filesystem:read',
                'name': 'Read from the filesystem',
                'default': True,
            },
            {
                'id': 'filesystem:write',
                'name': 'Write to the filesystem',
                'default': True,
            },
        ]