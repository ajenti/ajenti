#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='Ajenti',
    version='0.5-5',
    description='The server administration panel',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages = find_packages(),
    package_data={'': ['files/*.*', 'files/*/*.*', 'files/*/*/*.*', 'templates/*.*', 'widgets/*.*', 'layout/*.*']},
    scripts=['ajenti-panel', 'ajenti-pkg'],
    data_files=[
        ('/etc/ajenti', ['packaging/files/ajenti.conf']),
        ('/etc/init.d', ['packaging/files/ajenti']),
        ('/var/lib/ajenti/plugins', ['packaging/files/.placeholder']),
    ],
)
