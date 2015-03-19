import os
import pwd
import stat
import yaml

from aj.api import *


class BaseConfig(object):
    """
    A base class for config implementations. Your implementation must be able to save
    arbitrary mixture of ``dict``, ``list``, and scalar values.

    .. py:attribute:: data

        currenly loaded config content

    """
    def __init__(self):
        self.data = None

    def load(self):
        """
        Should load config content into :attr:`data`.
        """
        raise NotImplementedError()

    def save(self):
        """
        Should save config content from :attr:`data`.
        """
        raise NotImplementedError()


@service
class UserConfig(BaseConfig):
    def __init__(self, context):
        BaseConfig.__init__(self)
        username = pwd.getpwuid(os.getuid())[0]
        _dir = os.path.expanduser('~%s/.config' % username)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        self.path = os.path.join(_dir, 'ajenti.yml')
        if os.path.exists(self.path):
            self.load()
        else:
            self.data = {}

    def load(self):
        self.data = yaml.load(open(self.path))

    def harden(self):
        os.chmod(self.path, stat.S_IRWXU)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(
                self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True
            ))
        self.harden()
