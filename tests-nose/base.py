# pylint: skip-file
import atexit
import logging
import os
import requests
import time
import subprocess
import sys
import shutil


process = subprocess.Popen(['python', './ajenti-test-instance.py'])


def atexit_teardown():
    process.terminate()

atexit.register(atexit_teardown)
time.sleep(1)

url = 'http://localhost:8000'


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
        assert 'x-auth-identity' in rq.headers

    def not_found_test(self):
        rq = self.session.get(url + '/asdasdasd')
        assert rq.status_code == 404


class filesystem_test (base):
    dir = '/tmp/ajenti-filesystem-test'

    @classmethod
    def setup_class(cls):
        base.setup_class()
        if os.path.exists(cls.dir):
            shutil.rmtree(cls.dir)
        os.makedirs(cls.dir)

        with open(os.path.join(cls.dir, '1'), 'w') as f:
            f.write('file 1')

        with open(os.path.join(cls.dir, '2'), 'w') as f:
            f.write('file 2')

    @classmethod
    def teardown_class(cls):
        base.teardown_class()
        shutil.rmtree(cls.dir)

    def read_test(self):
        rq = self.session.get(url + '/api/filesystem/read/%s' % os.path.join(self.dir, '1'))
        assert rq.json() == 'file 1'

