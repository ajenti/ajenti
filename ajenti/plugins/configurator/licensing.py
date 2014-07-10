from ajenti.api import *
from ajenti.licensing import Licensing
from ajenti.plugins import manager
from ajenti.ui import UIElement, on


@plugin
class LicensingUI (UIElement):
    typeid = 'configurator:licensingui'

    def init(self):
        self.append(self.ui.inflate('configurator:licensing'))
        self.mgr = Licensing.get()

    def on_page_load(self):
        self.refresh()

    def on_tab_shown(self):
        self.refresh()

    def refresh(self):
        license_status = self.mgr.get_license_status()
        active = bool(self.mgr.get_license_status())
        self.find('license-active').visible = active
        self.find('license-inactive').visible = not active

        self.find('license-current-status').text = {
            'ok': 'OK',
            'invalid-key': _('Invalid key'),
            'invalid-ip': _('Invalid IP'),
            'expired': _('Expired'),
        }.get(license_status.get('status', None), _('Unknown'))

        license = license_status.get('license', {})
        self.find('license-current-expires').text = license.get('expires', '')
        self.find('license-current-type').text = license.get('type', '')
        self.find('license-current-company').text = license.get('company', '')

    @on('license-install', 'click')
    def on_install(self):
        try:
            self.mgr.write_license(self.find('license-key').value)
            self.mgr.activate()
        except Exception as e:
            self.context.notify('error', _('Error: "%s"') % str(e))
        self.refresh()

    @on('license-remove', 'click')
    def on_remove(self):
        try:
            self.mgr.deactivate()
            self.mgr.remove_license()
        except Exception as e:
            self.context.notify('error', _('Error: "%s"') % str(e))
        self.refresh()