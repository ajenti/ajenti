#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

import ajenti

__requires = filter(None, open('requirements.txt').read().splitlines())

exclusion = [
    'ajenti.plugins.elements',
    'ajenti.plugins.ltfs',
    'ajenti.plugins.ltfs*',
    'ajenti.plugins.vh',
    'ajenti.plugins.vh*',
    'ajenti.plugins.custom*',
    'ajenti.plugins.test*',
]

setup(
    name='ajenti',
    version=ajenti.__version__,
    install_requires=__requires,
    description='The server administration panel',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(exclude=['reconfigure', 'reconfigure.*'] + exclusion),
    package_data={'': ['content/*.*', 'content/*/*.*', 'content/*/*/*.*', 'layout/*.*', 'locales/*/*/*.mo']},
    scripts=['ajenti-panel', 'ajenti-ssl-gen', 'ajenti-ipc'],
    data_files=[
        ('/etc/ajenti', ['packaging/files/config.json']),
        ('/etc/init.d', ['packaging/files/ajenti']),
        ('/var/lib/ajenti/plugins', ['packaging/files/.placeholder']),
    ],
)
