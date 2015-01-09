import errno
import os

import aj
from aj.api import *
from aj.api.http import url, HttpPlugin

from aj.plugins.core.api.endpoint import endpoint


@component(HttpPlugin)
class Handler (HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/filesystem/read/(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_fs_read(self, http_context, path=None):
        return open(path).read()

    @url(r'/api/filesystem/write/(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_fs_write(self, http_context, path=None):
        with open(path, 'w') as f:
            f.write(http_context.body)

    @url(r'/api/filesystem/list/(?P<path>.+)')
    @endpoint(api=True)
    def handle_api_fs_list(self, http_context, path=None):
        items = []
        for name in os.listdir(path):
            item_path = os.path.join(path, name)
            accessError = None

            data = {
                'name': name,
                'path': item_path,
                'isDir': os.path.isdir(item_path),
                'isFile': os.path.isfile(item_path),
                'isLink': os.path.islink(item_path),            
            }

            try:
                stat = os.stat(item_path)
                data.update({
                    'mode': stat.st_mode,
                    'mtime': stat.st_mtime,
                    'uid': stat.st_uid,
                    'gid': stat.st_gid,
                    'size': stat.st_size,
                })
            except OSError as e:
                data['accessError'] = str(e)
                if e.errno == errno.ENOENT and os.path.islink(item_path):
                    data['brokenLink'] = True

            items.append(data)

        return {
            'parent': os.path.dirname(os.path.normpath(path)),
            'items': items,
        }
