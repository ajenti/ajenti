import os
import pwd
import stat
import yaml
from jadi import service


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

    def ensure_structure(self):
        self.data.setdefault('name', None)
        self.data.setdefault('max_sessions', 99)
        self.data.setdefault('language', 'en')
        self.data.setdefault('restricted_user', 'nobody')
        self.data.setdefault('auth', {})
        self.data['auth'].setdefault('emails', {})
        self.data['auth'].setdefault('provider', 'os')
        self.data.setdefault('ssl', {})
        self.data['ssl'].setdefault('enable', False)
        self.data['ssl'].setdefault('certificate', None)
        self.data['ssl'].setdefault('client_auth', {})
        self.data['ssl']['client_auth'].setdefault('enable', False)
        self.data['ssl']['client_auth'].setdefault('force', False)
        self.data['ssl']['client_auth'].setdefault('certificates', {})


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
