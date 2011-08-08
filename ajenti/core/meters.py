from ajenti.com import *
from ajenti.api import *
import json


class MetersExporter (Plugin, URLHandler):

    @url('^/api/meters$')
    def export(self, req, sr):
        clss = self.app.grab_plugins(IMeter)
        r = {}

        for cls in clss:
            variants = cls.get_variants()
            for v in variants:
                inst = cls.prepare(v)
                r.setdefault(cls.category, {}).setdefault(cls.plugin_id, []). \
                    append({
                        'name': inst.name,
                        'type': inst.type,
                        'text': inst.text,
                        'variant': v,
                        'transform': inst.transform,
                        'data': inst.format_value(),
                    })

        return json.dumps(r)
