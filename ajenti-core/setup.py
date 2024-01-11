#!/usr/bin/env python3
from setuptools import setup, find_packages
import platform

__requires = list(filter(None, open('requirements.txt').read().splitlines()))
if platform.python_implementation() == 'PyPy':
    __requires.append('git+git://github.com/schmir/gevent@pypy-hacks')
    __requires.append('git+git://github.com/gevent-on-pypy/pypycore ')
else:
    __requires.append('gevent>=1')

setup(
    name='aj-3',
    version='3.0.0',
    python_requires='>=3',
    install_requires=__requires,
    description='Web UI base toolkit',
    author='Daniel Schulz',
    author_email='info@schulz-informatik.com',
    url='https://schulz-informatik.com',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "aj": [
            "aj/static/images/*",
        ],
    },
)
