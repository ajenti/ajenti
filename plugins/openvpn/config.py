# coding=utf-8
"""OpenVPN plugin configuration backend"""
from ajenti.api import ModuleConfig
from backend import OpenVPNBackend

class OpenVPNConfig(ModuleConfig):
    """OpenVPN config"""
    target = OpenVPNBackend
    platform = ['any']

    labels = {
        'addr': 'Management address (host:port or path to UNIX socket)',
        'password': 'Management password'
    }

    addr = ''
    password = ''