# coding=utf-8
"""OpenVPN plugin"""
from ajenti.api import event, CategoryPlugin
from ajenti.ui import UI
from ajenti.utils import str_fsize
from time import ctime, sleep
from backend import OpenVPNBackend

class OpenVPNPlugin(CategoryPlugin):
    """OpenVPN plugin
    @ivar _b: Backend instance"""
    text = "OpenVPN"
    icon = "/dl/openvpn/icon.png"
    folder = "servers"

    def on_init(self):
        self._b = OpenVPNBackend(self.app)

    @event("button/click")
    def on_button_click(self, event, params, vars=None):
        try:
            if params[0] == "disconnect":
                # Disconnect tooltip clicked
                self.put_message("info", self._b.killbyaddr(params[1]))
            elif params[0] == "condRestart":
                # "Condional Restart" button clicked
                self.put_message("info", self._b.restartcond())
                sleep(2) # Give OpenVPN some time to reload
            elif params[0] == "hardRestart":
                # "Hard Restart" button clicked
                self.put_message("info", self._b.restarthard())
                sleep(2) # Give OpenVPN some time to reload
        except Exception, e:
            self.put_message("err", e)

    def get_ui(self):
        ui = self.app.inflate("openvpn:main")

        try:
            self._b.connect()
            status =   self._b.getstatus()
            stats =    self._b.getstats()
            messages = self._b.getmessages()
            self._b.disconnect()
        except Exception, e:
            self.put_message("err", e)
            return ui

        ui.find("nclients").set("text",   "Clients: {0}".format(stats["nclients"]))
        ui.find("bytesin").set( "text",  "Bytes in: {0}".format(str_fsize(float(stats["bytesin"]))))
        ui.find("bytesout").set("text", "Bytes out: {0}".format(str_fsize(float(stats["bytesout"]))))

        map(lambda c: ui.append("clients", UI.DTR(
            UI.Icon(icon="/dl/core/ui/stock/user.png"),
            UI.Label(text=c["cn"]),
            UI.Label(text=c["raddress"]),
            UI.Label(text=c["vaddress"]),
            UI.Label(text=str_fsize(float(c["brecv"]))),
            UI.Label(text=str_fsize(float(c["bsent"]))),
            UI.Label(text=c["connsince"]),
            UI.TipIcon(
                icon="/dl/core/ui/stock/delete.png",
                text="Disconnect",
                warning="Disconnect {0} ({1})?".format(c["cn"], c["raddress"]),
                id="disconnect/{0}".format(c["raddress"]))
        )), status["clients"])

        map(lambda m: ui.append("messages", UI.DTR(
            UI.Label(text=ctime(float(m[0]))),
            UI.Label(text=m[1]),
            UI.Label(text=m[2])
        )), messages)

        return ui
