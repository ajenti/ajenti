import os

import ajenti
from ajenti.api import *
from ajenti.api.http import url, HttpPlugin

from ajenti.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/filesystem/read/(?P<path>.+)')
    @endpoint(api=True, auth=False)
    def handle_api_fs_read(self, http_context, path=None):
        return open(path).read()

    @url(r'/api/filesystem/list/(?P<path>.+)')
    @endpoint(api=True, auth=False)
    def handle_api_fs_list(self, http_context, path=None):
        items = []
        for name in os.listdir(path):
            item_path = os.path.join(path, name)
            stat = os.stat(item_path)
            items.append({
                'name': name,
                'path': item_path,
                'isDir': os.path.isdir(item_path),
                'isFile': os.path.isfile(item_path),
                'isLink': os.path.islink(item_path),
                'mode': stat.st_mode,
                'mtime': stat.st_mtime,
                'uid': stat.st_uid,
                'gid': stat.st_gid,
                'size': stat.st_size,
            })

        return {
            'parent': os.path.dirname(os.path.normpath(path)),
            'items': items,
        }
