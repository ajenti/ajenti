from ajenti.api import *
from ajenti.com import *
import json


class Backend (Plugin):
    default_binary = { 'good_state': True }
    default_decimal = { 'limit_susp': 33.0, 'limit_dang': 66.0 }

    def __init__(self):
        self.cfg = self._get_cfg()

    def list_meters(self, category=None):
        return filter(lambda x:(not category)or(x.category==category),
             sorted(self.app.grab_plugins(IMeter), key=lambda x: x.name))

    def get_meter(self, cls, var):
        return filter(lambda x:x.plugin_id==cls, self.app.grab_plugins(IMeter))[0].prepare(var)

    def list_variated(self, x):
        for v in x.get_variants():
            x.prepare(v)
            yield x

    def _get_cfg(self):
        return json.loads(self.app.config.get('meters', 'config', '{}'))

    def _save_cfg(self):
        self.app.gconfig.set('meters', 'config', json.dumps(self.cfg))
        self.app.gconfig.save()

    def has_cfg(self, cls, var):
        return cls in self.cfg and var in self.cfg[cls]

    def get_cfg(self, cls, var):
        if not self.has_cfg(cls, var):
            return {}
        return self.cfg[cls][var]

    def set_cfg(self, cls, var, cfg):
        self.cfg.setdefault(cls, {})[var] = cfg
        self._save_cfg()

    def del_cfg(self, cls, var):
        del self.cfg[cls][var]
        if self.cfg[cls] == {}:
            del self.cfg[cls]
        self._save_cfg()
