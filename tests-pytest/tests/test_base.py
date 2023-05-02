# pylint: skip-file
import atexit
import logging
import json
import os
import requests
import time
import subprocess
import sys
import shutil
import pytest

url = 'http://localhost:8000'

@pytest.fixture(scope="session")
def handle_ajenti_process():
    print("\n--> Starting Ajenti")
    process = subprocess.Popen(['python3', './ajenti-test-instance.py'])
    while True:
        try:
            requests.get(url)
            break
        except:
            print('Ajenti is not ready yet, still waiting...')
            time.sleep(1)
    print("\n--> Ajenti started")
    yield
    os.system(f'kill {process.pid}')
    print("\n--> Ajenti stopped")

class TestBasicHttp:
    def test_identity(self, handle_ajenti_process):
        rq = requests.get(url)
        assert rq.status_code == 200
        assert 'x-auth-identity' in rq.headers

    def test_not_found(self):
        rq = requests.get(url + '/asdasdasd')
        assert rq.status_code == 404


class TestFilesystem:
    dir = '/tmp/ajenti-filesystem-test'

    def path(self, p):
        return os.path.join(self.dir, p)

    @pytest.fixture(scope="session")
    def tmp_dir(self):
        print("\n-->  Creating tmp dir")
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        yield
        print("\n-->  Removing tmp dir")
        shutil.rmtree(self.dir)

    def test_read(self, tmp_dir):
        with open(self.path('1'), 'w') as f:
            f.write('file 1')

        rq = requests.get(f'{url}/api/filesystem/read/{self.path("1")}?encoding=utf-8')
        assert rq.text == '"file 1"'
        rq = requests.get(f'{url}/api/filesystem/read/{self.path("3")}')
        assert rq.status_code == 404

    def test_write(self):
        content = 'file 2'
        rq = requests.post(
            f'{url}/api/filesystem/write/{self.path("2")}?encoding=utf-8',
            data=content
        )
        assert rq.status_code == 200
        with open(self.path('2')) as tmp2:
            assert tmp2.read() == content

    # def upload_test(self):
    #     content = 'uploaded stuff'
    #     with open(self.path('4'), 'w') as f:
    #         f.write(content)
    #     rq = self.session.post(
    #         f'{url}/api/filesystem/upload/{self.path("2")}',
    #         files={'upload': open(self.path('4'))}
    #     )
    #     assert rq.status_code, 200)
    #     assert open(self.path('2')).read(), content)

    def test_list(self):
        os.makedirs(self.path('list'))
        path = self.path('list/file')
        open(path, 'w').close()
        os.chmod(path, 0o765)
        rq = requests.get(f'{url}/api/filesystem/list/{self.path("list")}')
        assert rq.status_code == 200

        data = rq.json()['items']
        assert rq.json()['parent'] == self.dir

        assert len(data) == 1
        assert data[0]['name'] == 'file'
        assert data[0]['path'] == path
        assert data[0]['isDir'] == False
        assert data[0]['isFile'] == True
        assert data[0]['isLink'] == False
        assert data[0]['mode'] == 0o100765
        assert data[0]['uid'] == os.stat(path).st_uid
        assert data[0]['gid'] == os.stat(path).st_gid
        assert data[0]['size'] == 0

        shutil.rmtree(self.path('list'))

    def test_stat(self):
        path = self.path('file')
        open(path, 'w').close()
        os.chmod(path, 0o765)
        rq = requests.get(f'{url}/api/filesystem/stat/{path}')
        assert rq.status_code == 200

        data = rq.json()
        assert data['name'] == 'file'
        assert data['path'] == path
        assert data['isDir'] == False
        assert data['isFile'] == True
        assert data['isLink'] == False
        assert data['mode'] == 0o100765
        assert data['uid'] == os.stat(path).st_uid
        assert data['gid'] == os.stat(path).st_gid
        assert data['size'] == 0

    def test_chmod(self):
        path = self.path('file')
        open(path, 'w').close()
        os.chmod(path, 0o765)
        rq = requests.post(
            f'{url}/api/filesystem/chmod/{path}',
            data=json.dumps({'mode': 0o767})
        )
        assert rq.status_code == 200
        assert os.stat(path).st_mode, 0o100767

    def test_create_file(self):
        path = self.path('create_file_test')
        assert not os.path.exists(path)
        rq = requests.post(f'{url}/api/filesystem/create-file/{path}')
        assert rq.status_code == 200
        assert os.path.isfile(path)

    def test_create_dir(self):
        path = self.path('create_dir_test')
        assert not os.path.exists(path)
        rq = requests.post(f'{url}/api/filesystem/create-directory/{path}')
        assert rq.status_code == 200
        assert os.path.isdir(path)