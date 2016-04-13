# pylint: skip-file
from nose.tools import *
import atexit
import logging
import json
import os
import requests
import time
import subprocess
import sys
import shutil


process = subprocess.Popen(['python', './ajenti-test-instance.py'])
url = 'http://localhost:8000'


def atexit_teardown():
    process.terminate()

atexit.register(atexit_teardown)
while True:
    try:
        requests.get(url)
        break
    except:
        print 'ajenti not ready yet, waiting...'
        time.sleep(1)


class base (object):
    @classmethod
    def setup_class(cls):
        sys.stdout = open('/dev/stderr')
        cls.session = requests.Session()

    @classmethod
    def teardown_class(cls):
        pass


class basic_http_test (base):
    def identity_test(self):
        rq = self.session.get(url)
        eq_(rq.status_code, 200)
        assert 'x-auth-identity' in rq.headers

    def not_found_test(self):
        rq = self.session.get(url + '/asdasdasd')
        eq_(rq.status_code, 404)


class filesystem_test (base):
    dir = '/tmp/ajenti-filesystem-test'

    @classmethod
    def path(cls, p):
        return os.path.join(cls.dir, p)

    @classmethod
    def setup_class(cls):
        base.setup_class()
        if os.path.exists(cls.dir):
            shutil.rmtree(cls.dir)
        os.makedirs(cls.dir)

    @classmethod
    def teardown_class(cls):
        base.teardown_class()
        shutil.rmtree(cls.dir)

    def read_test(self):
        with open(self.path('1'), 'w') as f:
            f.write('file 1')

        rq = self.session.get(url + '/api/filesystem/read/%s' % self.path('1'))
        eq_(rq.text, 'file 1')
        rq = self.session.get(url + '/api/filesystem/read/%s' % self.path('3'))
        eq_(rq.status_code, 404)

    def write_test(self):
        content = 'file 2'
        rq = self.session.post(
            url + '/api/filesystem/write/%s' % self.path('2'),
            data=content
        )
        eq_(rq.status_code, 200)
        eq_(open(self.path('2')).read(), content)

    def upload_test(self):
        content = 'uploaded stuff'
        with open(self.path('4'), 'w') as f:
            f.write(content)
        rq = self.session.post(
            url + '/api/filesystem/upload/%s' % self.path('2'),
            files={'upload': open(self.path('4'))}
        )
        eq_(rq.status_code, 200)
        eq_(open(self.path('2')).read(), content)

    def list_test(self):
        os.makedirs(self.path('list'))
        path = self.path('list/file')
        open(path, 'w').close()
        os.chmod(path, 0765)
        rq = self.session.get(url + '/api/filesystem/list/%s' % self.path('list'))
        eq_(rq.status_code, 200)

        data = rq.json()['items']
        eq_(rq.json()['parent'], self.dir)

        eq_(len(data), 1)
        eq_(data[0]['name'], 'file')
        eq_(data[0]['path'], path)
        eq_(data[0]['isDir'], False)
        eq_(data[0]['isFile'], True)
        eq_(data[0]['isLink'], False)
        eq_(data[0]['mode'], 0100765)
        eq_(data[0]['uid'], os.stat(path).st_uid)
        eq_(data[0]['gid'], os.stat(path).st_gid)
        eq_(data[0]['size'], 0)

        shutil.rmtree(self.path('list'))

    def stat_test(self):
        path = self.path('file')
        open(path, 'w').close()
        os.chmod(path, 0765)
        rq = self.session.get(url + '/api/filesystem/stat/%s' % path)
        eq_(rq.status_code, 200)

        data = rq.json()
        eq_(data['name'], 'file')
        eq_(data['path'], path)
        eq_(data['isDir'], False)
        eq_(data['isFile'], True)
        eq_(data['isLink'], False)
        eq_(data['mode'], 0100765)
        eq_(data['uid'], os.stat(path).st_uid)
        eq_(data['gid'], os.stat(path).st_gid)
        eq_(data['size'], 0)

    def chmod_test(self):
        path = self.path('file')
        open(path, 'w').close()
        os.chmod(path, 0765)
        rq = self.session.post(url + '/api/filesystem/chmod/%s' % path, data=json.dumps({'mode': 0767}))
        eq_(rq.status_code, 200)
        eq_(os.stat(path).st_mode, 0100767)

    def create_file_test(self):
        path = self.path('create_file_test')
        ok_(not os.path.exists(path))
        rq = self.session.post(url + '/api/filesystem/create-file/%s' % path)
        eq_(rq.status_code, 200)
        ok_(os.path.isfile(path))

    def create_dir_test(self):
        path = self.path('create_dir_test')
        ok_(not os.path.exists(path))
        rq = self.session.post(url + '/api/filesystem/create-directory/%s' % path)
        eq_(rq.status_code, 200)
        ok_(os.path.isdir(path))
