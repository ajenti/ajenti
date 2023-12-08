#!/usr/bin/env python3
from setuptools import setup


setup(
    name='ajenti-dev-multitool',
    version='1.2.0',
    python_requires='>=3',
    install_requires=[
        'coloredlogs',
        'pyyaml',
        'gevent',
    ],
    description='-',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    scripts=['ajenti-dev-multitool'],
)
