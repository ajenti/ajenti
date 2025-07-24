#!/usr/bin/env python3
from setuptools import setup
from setuptools import find_packages


    # subprocess.call([sys.executable, 'ajenti-ssl-gen', socket.gethostname()], cwd=scripts_dir)



setup(
    name='ajenti-panel',
    version='2.2.11',
    python_requires='>=3',
    install_requires=[
        'aj==2.2.11',
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
)
