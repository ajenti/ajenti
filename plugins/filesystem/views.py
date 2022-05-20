"""
Tools to handle files, directories and uploads.
"""

import errno
import grp
import json
import os
import psutil
import pwd
import shutil
from jadi import component

from aj.api.http import get, post, HttpPlugin
from aj.api.endpoint import endpoint, EndpointError, EndpointReturn
from aj.auth import authorize


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context

    @get(r'/api/filesystem/mountpoints')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_mountpoints(self, http_context):
        """
        List all mountpoints.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: List of partitions
        :rtype: list of strings
        """

        return [x.mountpoint for x in psutil.disk_partitions()]

    @get(r'/api/filesystem/read/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_read(self, http_context, path=None):
        """
        Return the content of a file on the filesystem.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of the file
        :type path: string
        :return: Content of the file
        :rtype: string
        """

        if not os.path.exists(path):
            http_context.respond_not_found()
            return 'File not found'
        try:
            content = open(path, 'rb').read()
            if http_context.query:
                encoding = http_context.query.get('encoding', None)
                if encoding:
                    content = content.decode(encoding)
            return content
        except OSError as e:
            http_context.respond_server_error()
            return json.dumps({'error': str(e)})

    @post(r'/api/filesystem/write/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_write(self, http_context, path=None):
        """
        Write content (method post) to a specific file given with path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of the file
        :type path: string
        """

        try:
            content = http_context.body
            if http_context.query:
                encoding = http_context.query.get('encoding', None)
                if encoding:
                    content = content.decode('utf-8')
            with open(path, 'w') as f:
                f.write(content)
        except OSError as e:
            raise EndpointError(e)

    @get(r'/api/filesystem/upload')
    @authorize('filesystem:write')
    @endpoint(page=True)
    def handle_api_fs_get_upload_chunk(self, http_context):
        """
        Verify if the chunk part is present.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        id = http_context.query['flowIdentifier']
        chunk_index = http_context.query['flowChunkNumber']
        chunk_dir = f'/tmp/upload-{id}'
        try:
            os.makedirs(chunk_dir)
        except Exception as e:
            pass
        chunk_path = os.path.join(chunk_dir, chunk_index)

        if os.path.exists(chunk_path):
            http_context.respond('200 OK')
        else:
            http_context.respond('204 No Content')
        return ''

    @post(r'/api/filesystem/upload')
    @authorize('filesystem:write')
    @endpoint(page=True)
    def handle_api_fs_upload_chunk(self, http_context):
        """
        Write a chunk part of an upload in /tmp/upload*/<index>.

        :param http_context: HttpContext
        :type http_context: HttpContext
        """

        id = http_context.query['flowIdentifier']
        chunk_index = http_context.query['flowChunkNumber']
        chunk_dir = f'/tmp/upload-{id}'
        try:
            os.makedirs(chunk_dir)
        except Exception as e:
            pass
        chunk_path = os.path.join(chunk_dir, chunk_index)

        with open(chunk_path, 'wb') as f:
            f.write(http_context.query['file'])
        http_context.respond('200 OK')
        return ''

    @post(r'/api/filesystem/finish-upload')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_finish_upload(self, http_context):
        """
        Build all chunk parts from an uploaded file together and return it.
        Clean the tmp directory.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :return: Path of files
        :rtype: list of string
        """

        # files should be a list of dict
        files = http_context.json_body()
        targets = []

        for file in files:
            name = file['name']
            path = file['path']
            id = file['id']
            chunk_dir = f'/tmp/upload-{id}'

            target = os.path.join(path, name.replace('/', ''))
            with open(target, 'wb') as f:
                for i in range(len(os.listdir(chunk_dir))):
                    f.write(open(os.path.join(chunk_dir, str(i + 1)), 'rb').read())

            shutil.rmtree(chunk_dir)
            targets.append(target)
        return targets

    @get(r'/api/filesystem/list/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_list(self, http_context, path=None):
        """
        Return a list of objects (files, directories, ...) in a specific
        directory, and their informations.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Directory path
        :type path: string
        :return: All items with informations
        :rtype: dict
        """

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

    @get(r'/api/filesystem/stat/(?P<path>.+)')
    @authorize('filesystem:read')
    @endpoint(api=True)
    def handle_api_fs_stat(self, http_context, path=None):
        """
        Get all informations from a specific path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of file/directory
        :type path: string
        :return: POSIX permissions, size, type, ...
        :rtype: dict
        """

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

    @post(r'/api/filesystem/chmod/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_chmod(self, http_context, path=None):
        """
        Change mode for a specific file.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of file
        :type path: string
        """

        if not os.path.exists(path):
            raise EndpointReturn(404)
        data = json.loads(http_context.body.decode())
        try:
            os.chmod(path, data['mode'])
        except OSError as e:
            raise EndpointError(e)

    @post(r'/api/filesystem/create-file/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_create_file(self, http_context, path=None):
        """
        Create empty file on specified path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of file
        :type path: string
        """

        try:
            os.mknod(path, int('644', 8))
        except OSError as e:
            raise EndpointError(e)

    @post(r'/api/filesystem/create-directory/(?P<path>.+)')
    @authorize('filesystem:write')
    @endpoint(api=True)
    def handle_api_fs_create_directory(self, http_context, path=None):
        """
        Create empty directory on specified path.

        :param http_context: HttpContext
        :type http_context: HttpContext
        :param path: Path of directory
        :type path: string
        """

        try:
            os.makedirs(path)
        except OSError as e:
            raise EndpointError(e)
