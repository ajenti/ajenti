import logging
import sys
sys.path.insert(0, '../ajenti-core')

import aj
import aj.config
import aj.entry
import aj.log
import aj.plugins


class TestConfig(aj.config.BaseConfig):
    def __init__(self):
        aj.config.BaseConfig.__init__(self)
        self.data = {
            'bind': {
                'mode': 'tcp',
                'host': '0.0.0.0',
                'port': 8000,
            },
            'color': 'blue',
            'name': 'test',
            'ssl': {
                'enable': False
            }
        }

    def load(self):
        pass

    def save(self):
        pass


aj.log.init_console(logging.WARN)

aj.entry.start(
    config=TestConfig(),
    dev_mode=False,
    debug_mode=True,
    autologin=True,
    product_name='ajenti',
    daemonize=False,
    plugin_providers=[aj.plugins.DirectoryPluginProvider('../plugins')],
)
