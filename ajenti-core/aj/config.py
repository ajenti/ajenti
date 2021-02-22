import os
import pwd
import stat
import yaml
import logging
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
        self.data['auth'].setdefault('users_file', '/etc/ajenti/users.yml')
        self.data.setdefault('ssl', {})
        self.data['ssl'].setdefault('enable', False)
        self.data['ssl'].setdefault('certificate', None)
        self.data['ssl'].setdefault('fqdn_certificate', None)
        self.data['ssl'].setdefault('client_auth', {})
        self.data['ssl']['client_auth'].setdefault('enable', False)
        self.data['ssl']['client_auth'].setdefault('force', False)
        self.data['ssl']['client_auth'].setdefault('certificates', {})

        # Before Ajenti 2.1.38, the users were stored in config.yml
        if 'users' in self.data['auth'].keys():
            logging.warning("Users should be stored in %s, migrating it ...", self.data['auth']['users_file'])
            self.migrate_users_to_own_configfile()

    def migrate_users_to_own_configfile(self):
        users_path = self.data['auth']['users_file']

        if os.path.isfile(users_path):
            logging.info("%s already existing, backing it up", users_path)
            os.rename(users_path, users_path + '.bak')

        to_write = {'users': self.data['auth']['users']}
        with open(users_path, 'w') as f:
           f.write(yaml.safe_dump(to_write, default_flow_style=False, encoding='utf-8', allow_unicode=True).decode('utf-8'))

        del self.data['auth']['users']
        self.save()
        logging.info("%s correctly written", users_path)


    def get_non_sensitive_data(self):
        return {
            'color': self.data['color'],
            'language': self.data['language'],
            'name': self.data['name']
        }

class AjentiUsers(BaseConfig):
    def __init__(self, path):
        BaseConfig.__init__(self)
        self.data = None
        self.path = os.path.abspath(path)

    def __str__(self):
        return self.path

    def load(self):
        # Find default users file
        if not self.path:
            # Check for users file in /etc/ajenti/users.yml
            if os.path.isfile('/etc/ajenti/users.yml'):
                config_path = '/etc/ajenti/users.yml'
            elif os.path.isfile(os.path.join(sys.path[0], 'users.yml')):
                # Try local users file
                config_path = os.path.join(sys.path[0], 'users.yml')

        if not os.path.exists(self.path):
            logging.error('Users file "%s" not found', self.path)

        if os.geteuid() == 0:
            os.chmod(self.path, 384)  # 0o600
        self.data = yaml.load(open(self.path), Loader=yaml.SafeLoader)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True).decode('utf-8'))

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
        self.data = yaml.load(open(self.path), Loader=yaml.SafeLoader)

    def harden(self):
        os.chmod(self.path, stat.S_IRWXU)

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.safe_dump(
                self.data, default_flow_style=False, encoding='utf-8', allow_unicode=True
            ).decode('utf-8'))
        self.harden()
