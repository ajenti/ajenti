import os
import pwd
import stat
import yaml
from jadi import interface, component, service
import aj
from aj.util import public


class BaseConfig():
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
        self.data.setdefault('session_max_time', 3600)
        self.data.setdefault('language', 'en')
        self.data.setdefault('restricted_user', 'nobody')
        self.data.setdefault('auth', {})
        self.data['auth'].setdefault('emails', {})
        self.data['auth'].setdefault('provider', 'os')
        self.data['auth'].setdefault('user_config', 'os')
        self.data.setdefault('ssl', {})
        self.data['ssl'].setdefault('enable', False)
        self.data['ssl'].setdefault('certificate', None)
        self.data['ssl'].setdefault('fqdn_certificate', None)
        self.data['ssl'].setdefault('client_auth', {})
        self.data['ssl']['client_auth'].setdefault('enable', False)
        self.data['ssl']['client_auth'].setdefault('force', False)
        self.data['ssl']['client_auth'].setdefault('certificates', {})

@interface
class UserConfigProvider():
    id = None
    name = None

    def __init__(self, context):
        self.data = None

    def load(self):
        raise NotImplementedError

    def harden(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

class UserConfigError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

@public
@service
class UserConfigService():
    def __init__(self, context):
        self.context = context

    def get_provider(self):
        provider_id = aj.config.data['auth'].get('user_config', 'os')
        for provider in UserConfigProvider.all(self.context):
            if provider.id == provider_id:
                return provider
        raise UserConfigError('User config provider %s is unavailable' % provider_id)

@component(UserConfigProvider)
class UserConfig(UserConfigProvider):
    id = 'os'
    name = 'OS users'

    def __init__(self, context):
        UserConfigProvider.__init__(self, context)
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
        self.data = yaml.load(open(self.path), Loader=yaml.Loader)

    def harden(self):
        os.chmod(self.path, stat.S_IRWXU)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(
                self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True
            ).decode('utf-8'))
        self.harden()
