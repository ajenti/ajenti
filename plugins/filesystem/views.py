import errno
import grp
import json
import os
import psutil
import pwd
import shutil
from jadi import component

from aj.api.http import url, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @url(r'/api/filesystem/mountpoints')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_mountpoints(self, http_context):
        return [x.mountpoint for x in psutil.disk_partitions()]

    @url(r'/api/filesystem/read/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_read(self, http_context, path=None):
        if not os.path.exists(path):
            return http_context.respond_not_found()
        try:
            content = open(path).read()
            if http_context.query:
                encoding = http_context.query.get('encoding', None)
                if encoding:
                    content = content.decode(encoding).encode('utf-8')
            return content
        except OSError as e:
            http_context.respond_server_error()
            return json.dumps({'error': str(e)})

    @url(r'/api/filesystem/write/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_write(self, http_context, path=None):
        try:
            content = http_context.body
            if http_context.query:
                encoding = http_context.query.get('encoding', None)
                if encoding:
                    content = content.decode('utf-8').encode(encoding)
            with open(path, 'w') as f:
                f.write(content)
        except OSError as e:
            raise EndpointError(e)

    @url(r'/api/filesystem/upload')
    @authorize('filesystem:write')
    @endpoint(page=True)
    def handle_api_fs_upload_chunk(self, http_context):
        id = http_context.query['flowIdentifier']
        chunk_index = http_context.query['flowChunkNumber']
        chunk_dir = '/tmp/upload-%s' % id
        try:
            os.makedirs(chunk_dir)
        except:
            pass
        chunk_path = os.path.join(chunk_dir, chunk_index)

        if http_context.method == 'GET':
            if os.path.exists(chunk_path):
                http_context.respond('200 OK')
            else:
                http_context.respond('204 No Content')
        else:
            with open(chunk_path, 'w') as f:
                f.write(http_context.query['file'])
            http_context.respond('200 OK')
        return ''

    @url(r'/api/filesystem/finish-upload')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_finish_upload(self, http_context):
        name = http_context.json_body()['name']
        path = http_context.json_body()['path']
        id = http_context.json_body()['id']
        chunk_dir = '/tmp/upload-%s' % id

        target = os.path.join(path, name.replace('/', ''))
        with open(target, 'wb') as f:
            for i in range(len(os.listdir(chunk_dir))):
                f.write(open(os.path.join(chunk_dir, str(i + 1))).read())

        shutil.rmtree(chunk_dir)
        return target

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
