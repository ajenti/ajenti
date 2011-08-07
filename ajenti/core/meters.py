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
                cls.prepare(v)
                r.setdefault(cls.category, {}).setdefault(cls.plugin_id, []). \
                    append({
                        'name': cls.name,
                        'type': cls.type,
                        'text': cls.text,
                        'variant': v,
                        'data': cls.format_value(),
                    })

        return json.dumps(r)
