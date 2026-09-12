#!/usr/bin/env python3
from setuptools import setup, find_packages

__requires = list(filter(None, open('requirements.txt').read().splitlines()))

setup(
    name='aj',
    version='2.2.17',
    python_requires='>=3',
    install_requires=__requires,
    description='Web UI base toolkit',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='https://ajenti.org/',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "aj": [
            "aj/static/images/*",
        ],
    },
)
