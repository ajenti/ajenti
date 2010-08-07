from ajenti import apis
from ajenti.com import *
from ajenti.ui import *
from ajenti.app.urlhandler import URLHandler, url
from ajenti.utils import wsgi_serve_file, shell

import os

class SquidReports(Plugin, URLHandler):
    implements(apis.squid.IPluginPart)
    
    weight = 20
    title = 'Reports'

    tab = 0
    cfg = 0
    parent = None
        
    def init(self, parent, cfg, tab):
        self.parent = parent
        self.cfg = cfg
        self.tab = tab
   
    @url('^/sarg_report/.+$') 
    def process(self, req, start_response):
        file = os.path.join('/var/lib/sarg/', req['PATH_INFO'][13:])
        return wsgi_serve_file(req, start_response, file)        
        
    def get_ui(self):
        vc = UI.VContainer(
                UI.Button(text='Generate report', id='gen'),
                UI.Spacer(height=10),
                UI.IFrame(src='/sarg_report/index.html', width="600", height="500")
             )
        return vc

    def on_click(self, event, params, vars=None):
        if params[0] == 'gen':
            self.parent._tab = self.tab
            shell('sarg')

    def on_submit(self, event, params, vars=None):
        pass
