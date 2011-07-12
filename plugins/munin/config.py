from ajenti.api import ModuleConfig
from client import MuninClient


class GeneralConfig(ModuleConfig):
    target = MuninClient
    platform = ['any']

    labels = {
        'url': 'Base Munin URL',
        'username': 'HTTP username',
        'password': 'HTTP password',
    }

    url = 'http://localhost/munin'
    username = ''
    password = ''
