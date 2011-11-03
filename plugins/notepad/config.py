from ajenti.api import ModuleConfig
from main import *


class GeneralConfig(ModuleConfig):
    target = NotepadPlugin
    platform = ['any']

    labels = {
        'dir': 'Initial directory'
    }

    dir = '/etc'
    _chroot = None
