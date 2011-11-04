from ajenti.api import *
from ajenti.com import *
import threading
import json



class HealthMonitor (Component):
    name = 'health-monitor'

    def on_starting(self):
        self._cond_refresh = threading.Condition()
        self._cond_refreshed = threading.Condition()
        self._lock_refresh = threading.Lock()
        self._state = {}

    def refresh(self):
        self._lock_refresh.acquire()
        self._cond_refresh.acquire()
        self._cond_refresh.notify()
        self._cond_refresh.release()
        self._lock_refresh.release()
        self._cond_refreshed.acquire()
        self._cond_refreshed.wait()
        self._cond_refreshed.release()
        
    def iterate(self):
        cfg = json.loads(self.app.gconfig.get('meters', 'config'))
        res = {}
        for cls in cfg:
            try:
                inst = self.app.grab_plugins(IMeter, lambda x:x.plugin_id==cls)[0]
                for var in cfg[cls]:
                    constr = cfg[cls][var]
                    i = inst.prepare(var)
                    res[i] = getattr(self, 'validate_%s'%i.type)(i.format_value(), constr)
            except:
                pass
        self._state = res

    def get(self):
        return self._state

    def run(self):
        while True:
            self._cond_refresh.acquire()
            try:
                self.iterate()
            except:
                pass
            self._cond_refresh.release()

            self._cond_refreshed.acquire()
            self._cond_refreshed.notify()
            self._cond_refreshed.release()
            self._cond_refresh.acquire()
            self._cond_refresh.wait(1000*60*5)
            self._cond_refresh.release()

    def validate_binary(self, val, cfg):
        return 'good' if val['value'] == cfg['good_state'] else 'dang'

    def validate_decimal(self, val, cfg):
        if cfg['limit_susp'] < cfg['limit_dang']:
            if val['value'] < cfg['limit_susp']:
                return 'good'
            if val['value'] > cfg['limit_dang']:
                return 'dang'
        if cfg['limit_susp'] > cfg['limit_dang']:
            if val['value'] > cfg['limit_susp']:
                return 'good'
            if val['value'] < cfg['limit_dang']:
                return 'dang'
        return 'susp'

    validate_linear = validate_decimal



class MetersExporter (Plugin, URLHandler):

    @url('^/api/meters$')
    def export(self, req, sr):
        clss = self.app.grab_plugins(IMeter)
        r = {}

        for cls in clss:
            variants = cls.get_variants()
            for v in variants:
                inst = cls.prepare(v)
                r.setdefault(cls.category, {}).setdefault(cls.plugin_id, {})[v] = \
                    {
                        'name': inst.name,
                        'mtype': inst.type,
                        'text': inst.text,
                        'variant': v,
                        'transform': inst.transform,
                        'data': inst.format_value(),
                    }

        return json.dumps(r)



class HealthExporter (Plugin, URLHandler):

    @url('^/api/health$')
    def export(self, req, sr):
        mon = ComponentManager.get().find('health-monitor')
        data = json.loads(self.app.gconfig.get('meters', 'config', '{}'))
        nd = {}
        mon.refresh()
        for i in mon.get():
            nd.setdefault(i.category, {}).setdefault(i.plugin_id, {})[i.variant] = {
                'value': i.format_value(),
                'info': {
                    'text': i.text,
                    'name': i.name,
                    'type': i.type,
                    'variant': i.variant,
                    'transform': i.transform,
                },
                'contraints': data[i.plugin_id][i.variant],
                'state': mon.get()[i],
            }
        return json.dumps(nd)
