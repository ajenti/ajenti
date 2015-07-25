import errno
import grp
import json
import os
import pwd
from jadi import component

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/filesystem/read/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_read(self, http_context, path=None):
        if not os.path.exists(path):
            raise EndpointReturn(404)
        try:
            return open(path).read()
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/write/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_write(self, http_context, path=None):
        try:
            with open(path, 'w') as f:
                f.write(http_context.body)
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/upload/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_upload(self, http_context, path=None):
        try:
            with open(path, 'w') as f:
                f.write(http_context.query['upload'])
        except OSError as e:
            raise EndpointError(e)
        return True

    @url(r'/api/filesystem/list/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_list(self, http_context, path=None):
        if not os.path.exists(path):
            raise EndpointReturn(404)
        try:
            items = []
            for name in os.listdir(path):
                item_path = os.path.join(path, name)

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
                'parent': os.path.dirname(os.path.normpath(path)) if path != '/' else None,
                'items': items,
            }
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/stat/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_stat(self, http_context, path=None):
        if not os.path.exists(path):
            raise EndpointReturn(404)
        data = {
            'name': os.path.split(path)[1],
            'path': path,
            'isDir': os.path.isdir(path),
            'isFile': os.path.isfile(path),
            'isLink': os.path.islink(path),
            'readAccess': os.access(path, os.R_OK),
            'writeAccess': os.access(path, os.W_OK),
            'executeAccess': os.access(path, os.X_OK),
        }

        try:
            stat = os.stat(path)
            data.update({
                'mode': stat.st_mode,
                'mtime': stat.st_mtime,
                'uid': stat.st_uid,
                'gid': stat.st_gid,
                'size': stat.st_size,
            })

            try:
                data['user'] = pwd.getpwuid(stat.st_uid).pw_name
            except KeyError:
                pass

            try:
                data['group'] = grp.getgrgid(stat.st_gid).gr_name
            except KeyError:
                pass
        except OSError as e:
            data['accessError'] = str(e)
            if e.errno == errno.ENOENT and os.path.islink(path):
                data['brokenLink'] = True

        return data

    @url(r'/api/filesystem/chmod/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_chmod(self, http_context, path=None):
        if not os.path.exists(path):
            raise EndpointReturn(404)
        data = json.loads(http_context.body)
        try:
            os.chmod(path, data['mode'])
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/create-file/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_create_file(self, http_context, path=None):
        try:
            os.mknod(path, int('644', 8))
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/create-directory/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_create_directory(self, http_context, path=None):
        try:
            os.makedirs(path)
        except OSError as e:
            raise EndpointError(e)
