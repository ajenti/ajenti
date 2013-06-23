#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

import ajenti.build

__version = ajenti.build.version

setup(
    name='ajenti',
    version=__version,
    install_requires=[
        'pyOpenSSL',
        'gevent',
        'gevent-socketio',
        'lxml>=2.2.4',
        'python-daemon',
        'passlib',
        'psutil>=0.6.0',
    ],
    description='The server administration panel',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(exclude=['reconfigure', 'reconfigure.*']),
    package_data={'': ['content/*.*', 'content/*/*.*', 'content/*/*/*.*', 'layout/*.*', 'locale/*/*/*.mo']},
    scripts=['ajenti-panel', 'ajenti-ssl-gen'],
    data_files=[
        ('/etc/ajenti', ['packaging/files/config.json']),
        ('/etc/init.d', ['packaging/files/ajenti']),
        ('/var/lib/ajenti/plugins', ['packaging/files/.placeholder']),
    ],
)
