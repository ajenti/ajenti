#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='ajenti',
    version='0.6.1',
    install_requires=[
        'pyOpenSSL',
        'gevent',
        'lxml>=2.2.4',
    ],
    description='The server administration panel',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages = find_packages(),
    package_data={'': ['files/*.*', 'files/*/*.*', 'files/*/*/*.*', 'templates/*.*', 'widgets/*.*', 'layout/*.*']},
    scripts=['ajenti-panel', 'ajenti-pkg'],
    data_files=[
        ('/etc/ajenti', ['packaging/files/ajenti.conf']),
        ('/etc/ajenti/users', ['packaging/files/admin.conf']),
        ('/etc/init.d', ['packaging/files/ajenti']),
        ('/var/lib/ajenti/plugins', ['packaging/files/.placeholder']),
    ],
)
