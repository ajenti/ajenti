#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools import find_packages

import os
import socket
import subprocess

import aj


def _pre_install (dir):
    platform = None
    if os.path.exists('/etc/redhat-release'):
        platform = 'rhel'
    if os.path.exists('/etc/debian_version'):
        platform = 'debian'
    if not platform:
        print ' *** Could not detect your distribution!'
        print ' *** We won\'t be able to install some dependencies automatically.'
        print ' *** Press Enter if you know what you are doing, press Ctrl-C to abort.'
        raw_input()
        return

    if platform == 'rhel':
        subprocess.call('yum install -y gcc make python-devel libxslt-devel libxml2-devel libffi-devel openssl-devel libjpeg-turbo-devel libpng-devel dbus-python', shell=True)
    if platform == 'rhel':
        subprocess.call('apt-get install -y build-essential python-dev libxslt1-dev libxml2-dev libffi-dev libssl-dev libjpeg-dev libpng-dev', shell=True)


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
        self.execute(_pre_install, [self.install_lib], msg='Running pre install script')
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
