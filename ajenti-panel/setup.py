#!/usr/bin/env python3
from setuptools import setup
from setuptools.command.install import install as _install
from setuptools import find_packages

import os
import socket
import subprocess
import sys


def _post_install(scripts_dir):
    config_path = '/etc/ajenti/config.yml'
    users_file = '/etc/ajenti/users.yml'

    if not os.path.exists('/etc/ajenti'):
        os.makedirs('/etc/ajenti')
    if not os.path.exists(config_path):
        with open(config_path, 'w') as c:
            c.write(f'''
auth:
  allow_sudo: true
  emails: {{}}
  provider: os
  users_file: {users_file}
bind:
  host: 0.0.0.0
  mode: tcp
  port: 8000
color: default
max_sessions: 9
trusted_domains: []
trusted_proxies: []
session_max_time: 3600
name: {socket.gethostname()}
ssl:
  certificate:
  fqdn_certificate:
  force: false
  client_auth:
    certificates: []
    enable: false
    force: false
  enable: false
        ''')

    if not os.path.exists(users_file):
        with open(users_file, 'w') as u:
            u.write("users: null")
    subprocess.call([sys.executable, 'ajenti-ssl-gen', socket.gethostname()], cwd=scripts_dir)


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, [self.install_scripts], msg='Running post install script')


setup(
    name='ajenti-panel',
    version='2.2.1',
    python_requires='>=3',
    install_requires=[
        'aj==2.2.1',
        'pyyaml',
        'requests',
    ],
    description='Ajenti core based panel',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='https://ajenti.org/',
    packages=find_packages(),
    package_data={
        "": [
            "static/images/error.jpeg",
            "static/images/Logo.png",
            "static/emails/reset_email.html",
        ]},
    scripts=['ajenti-panel', 'ajenti-ssl-gen', 'ajenti-client-ssl-gen', 'ajenti-upgrade'],
    cmdclass={'install': install},
)
