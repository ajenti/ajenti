# coding=utf-8
"""OpenVPN widget"""
from ajenti.com import implements, Plugin
from ajenti import apis
from ajenti.utils import str_fsize
from backend import OpenVPNBackend

#noinspection PyUnusedLocal
class OpenVPNWidget(Plugin):
    """OpenVPN Widget
    @ivar _b: Backend instance"""
    implements(apis.dashboard.IWidget)
    icon = "/dl/openvpn/icon.png"
    name = "OpenVPN"
    title = "OpenVPN"
    style = "normal"

    def __init__(self, *args, **kwargs):
        self._b = OpenVPNBackend(self.app)

    def get_ui(self, cfg, id = None):
        s = self._b.getstats()
        ui = self.app.inflate("openvpn:widget")
        ui.find("nclients").set("text", s["nclients"])
        ui.find("bytesin").set("text", str_fsize(float(s["bytesin"])))
        ui.find("bytesout").set("text", str_fsize(float(s["bytesout"])))
        return ui

    def get_config_dialog(self):
        return None

    def handle(self, event, params, cfg, vars=None):
        pass

    def process_config(self, vars):
        pass
 