from ajenti.api import *
from ajenti.utils import *
from ajenti.ui import *
from ajenti.plugins.core.api import *
from ajenti import apis

from backend import *


class BaculaDirPlugin(apis.services.ServiceControlPlugin):
    text = 'Bacula Director'
    icon = '/dl/bacula_dir/icon.png'
    folder = 'apps'
    service_name = 'bacula-director'

    def on_init(self):
        self.dir = Director(self.app) 
        
    def get_main_ui(self):
        ui = self.app.inflate('bacula_dir:main')
        st = self.dir.get_status()

        for x in st['scheduled']:
            ui.append('scheduled', UI.DTR(
                UI.Label(text=x['name']),
                UI.Label(text=x['level']),
                UI.Label(text=x['volume']),
                UI.Label(text=x['date']),
                UI.Label(text=x['type']),
                UI.HContainer(
                    UI.TipIcon(
                        id='run/%s'%x['name'],
                        text='Run job',
                        icon='/dl/core/ui/stock/service-run.png'
                    ),
                    UI.TipIcon(
                        id='edit/%s'%x['name'],
                        text='Edit job',
                        icon='/dl/core/ui/stock/edit.png'
                    ),
                    UI.TipIcon(
                        id='delete/%s'%x['name'],
                        text='Delete job',
                        icon='/dl/core/ui/stock/delete.png'
                    ),
                )
            ))

        for x in st['running']:
            ui.append('running', UI.DTR(
                UI.Label(text=x['id']),
                UI.Label(text=x['name']),
                UI.Label(text=x['level']),
                UI.HContainer(
                    UI.TipIcon(
                        id='stop/%s',
                        text='Cancel job',
                        icon='/dl/core/ui/stock/service-stop.png'
                    )
                )
            ))

        for x in st['terminated']:
            ui.append('terminated', UI.DTR(
                UI.StatusCell(text=x['status'], status='info' if (x['status']=='OK') else 'err'),
                UI.Label(text=x['name']),
                UI.Label(text=x['id']),
                UI.Label(text=x['level']),
                UI.Label(text=x['files']),
                UI.Label(text=x['bytes']),
                UI.Label(text=x['finished']),
                None
            ))
        return ui
   
    @event('button/click')
    def on_click(self, event, params, vars=None):
        if params[0] == 'run':
            self.dir.run_job(params[1])