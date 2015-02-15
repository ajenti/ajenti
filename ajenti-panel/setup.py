#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools import find_packages

import os
import socket
import subprocess

import aj


def _post_install (dir):
    config_path = '/etc/ajenti/config.yml'
    if not os.path.exists('/etc/ajenti'):
        os.makedirs('/etc/ajenti')
    if not os.path.exists(config_path):
        open(config_path, 'w').write('''
bind:
  host: 0.0.0.0
  mode: tcp
  port: 8000
color: default
emails:
name: %s
ssl:
  certificate:
  client_auth:
    certificates: []
    enable: false
    force: false
  enable: false
''' % socket.gethostname())
    subprocess.call(['ajenti-ssl-gen', socket.gethostname()])



class install (_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, [self.install_lib], msg='Running post install script')


setup(
    name='ajenti-panel',
    version=aj.__version__,
    install_requires=[
        'aj==%s' % aj.__version__,
        'pyyaml',
    ],
    description='Ajenti core based panel',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(),
    scripts=['ajenti-panel', 'ajenti-ssl-gen', 'ajenti-client-ssl-gen'],
    cmdclass={'install': install},
)
