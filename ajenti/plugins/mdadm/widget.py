# coding=utf-8
# ---------------------------------------------------------------------------
# MDADM plugin for Ajenti, to manage the MD devices.
#
#   Copyright (C) 2015 Marc Bertens <m.bertens@pe2mbs.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see http://www.gnu.org/licenses/agpl-3.0.html.
# ---------------------------------------------------------------------------
#
import logging

from ajenti.api import plugin
from ajenti.api.sensors import Sensor
from ajenti.plugins.dashboard.api import DashboardWidget
from api import getMdadmStatus


log = logging.getLogger()


@plugin
class MdadmSensor(Sensor):
    id = 'mdadm'
    timeout = 5

    def measure(self, variant):
        mdadm = getMdadmStatus()
        mdadm.Update()
        return mdadm
    # end def


# end class

@plugin
class MdadmWidget(DashboardWidget):
    name = _('MDADM status')
    icon = 'hdd'

    def init(self):
        self.sensor = Sensor.find('mdadm')
        self.append(self.ui.inflate('mdadm:mdadm-widget'))
        self.find('icon').icon = 'hdd'
        self.find('name').text = _('MDADM status')

        mdadm = self.sensor.value()

        for device in mdadm.Devices:
            line = self.ui.inflate('mdadm:mdadm-widget-line')
            line.find('device').text = device.name
            status = line.find('status')
            progress = line.find('progress')
            progress.visible = ( device.showRecovery )
            if progress.visible:
                log.debug("progress.value: '%s' = '%s'" % ( device.progress, device.progress / 100 ))
                progress.value = float(device.progress / 100)
                log.debug("progress.value: '%f'" % ( progress.value ))
            # end if
            status.text = device.stateText
            self.find('lines').append(line)
        # next
    # end def
# end class