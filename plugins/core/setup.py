from setuptools import setup, find_packages

import os

__requires = [dep.split('#')[0].strip() for dep in filter(None, open('requirements.txt').read().splitlines())] 

setup(
    name='ajenti.plugin.core',
    version='0.1',
    python_requires='>=3',
    install_requires=__requires,
    description='Core',
    long_description='A Core plugin for Ajenti panel',
    author='KIENTZ',
    author_email='moi',
    url='moi',
    packages=find_packages(),
    include_package_data=True,
)
