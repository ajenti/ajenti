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

from ajenti.api import *
from ajenti.plugins.mdadm import GetPluginVersion, GetAuthor, GetEmail, GetCopyright
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on, p, UIElement
from ajenti.ui.binder import Binder
from api import getMdadmStatus, RAID_Device, NewRaidDevice


@plugin
class RAID(SectionPlugin):
    platforms = ['debian']

    raid_types = [( 0, 'RAID0' ),
                  ( 1, 'RAID1' ),
                  ( 2, 'RAID2' ),
                  ( 3, 'RAID3' ),
                  ( 4, 'RAID4' ),
                  ( 5, 'RAID5' ),
                  ( 6, 'RAID6' )]

    def getPartions(self):
        data = open('/proc/partitions').readlines()
        data = data[2:]
        device_names = []
        for device in self.mdadm.Devices:
            device_names.append(device.name)
            for drive in device.devices:
                device_names.append(drive.name)
            # next
        # next
        partions = []
        for line in data:
            line = line.strip(' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace('\n', '')
            cols = line.split(' ')
            if len(cols) == 4:
                if not "/dev/%s" % ( cols[3] ) in device_names:
                    partions.append("/dev/%s" % ( cols[3] ))
                # end if
            # end if
        # next
        partions.sort()
        return partions

    # end def

    def init(self):
        self.log = logging.getLogger()
        self.title = _('MDADM')
        self.icon = 'hdd'
        self.category = _('System')
        self.TabBinders = []
        self.mdadm = getMdadmStatus()
        """
            Make sure we have an up-to date MDADM class
        """
        self.mdadm.Update()
        self.NewRaid = NewRaidDevice(self.mdadm)
        self.append(self.ui.inflate('mdadm:main'))
        newRaidTab = self.find('new_raid_device')
        newRaidTab.find('create_raid').on('click', self.on_createNewRaid)
        raidtype = newRaidTab.find('raid_types')
        raidtype.values = []
        raidtype.labels = []
        for value, label in self.raid_types:
            raidtype.values.append(value)
            raidtype.labels.append(label)
        # next
        newDevices = newRaidTab.find('new_devices')
        adn = newRaidTab.find('active_device_names')
        adn.values = adn.labels = self.getPartions()
        adt = newRaidTab.find('active_device_type')
        adt.values = adt.labels = ['Active', 'Spare']

        def post_new_drive_device(obj, coll, item, ui):
            ui.find('remove_new').on('click', self.on_remove_new, obj, coll, item)
            ui.find('update_new').on('click', self.on_update_new, obj, coll, item)
            return

        # end if

        def post_update_drive_device(obj, coll, item, ui):
            adn = ui.find('active_device_names')
            adn.value = adn.label = item.drive_name
            adt = ui.find('active_device_type')
            adt.value = adt.label = item.drive_type
            return

        # end def

        def post_new_item(obj, coll):
            return RAID_Device(obj)

        # end def

        newDevices.post_item_bind = post_new_drive_device
        newDevices.post_item_update = post_update_drive_device
        newDevices.new_item = lambda c: post_new_item(self.mdadm, c)
        self.TabCount = 1
        self.TabBinders.append(( self.NewRaid, None, Binder(self.NewRaid, newRaidTab) ))
        self.find('onupdate').on('click', self.onUpdate)
        header = self.find('header')
        header.version = self.mdadm.getVersion()
        header.title = 'RAID'
        header.plugin = 'mdadm'
        header.author = GetAuthor()
        header.pluginversion = GetPluginVersion()
        header.email = GetEmail()
        header.copyright = GetCopyright()
        tabs = self.find('insert_tabs')

        def post_drive_device(obj, coll, item, ui):
            ui.find('fail-device').on('click', self.on_failDevice, obj, item)
            ui.find('remove-device').on('click', self.on_removeDevice, obj, item)
            return

        # end def

        for device in self.mdadm.Devices:
            tabTemplate = self.ui.inflate('mdadm:mdadm-tab')
            devTab = tabTemplate.find("device_tab")
            devTab.title = device.name
            devTab.id = device.name

            self.TabBinders.append(( device, devTab, Binder(device, devTab) ))

            devTab.find('addDrive').on('click', self.on_addDevice, device)
            devTab.find('startDevice').on('click', self.on_startDevice, device)
            devTab.find('stopDevice').on('click', self.on_stopDevice, device)
            drive_devices = devTab.find('drive_devices')
            drive_devices.post_item_bind = post_drive_device

            tabs.append(tabTemplate)
            self.TabCount += 1
        # next
        tabs.active = 1
        self.refresh()
        return

    # end def

    def on_createNewRaid(self):
        binder = self.TabBinders[0][2]
        binder.update()
        binder.setup(self.TabBinders[0][0]).populate()
        active_devices = []
        spare_devices = []
        for dev in self.NewRaid.new_devices:
            if dev.drive_type == "Active":
                active_devices.append(dev.drive_name)
            else:
                spare_devices.append(dev.drive_name)
            # end if
        # next
        status, msg = self.mdadm.createDevice(self.NewRaid.device_name, self.NewRaid.device_type,
                                              self.NewRaid.meta_data, active_devices, spare_devices,
                                              ( self.NewRaid.enable_mon, self.NewRaid.email ))
        if status:
            if "error" in msg:
                self.context.notify('error', msg)
            else:
                self.context.notify('info', msg)
            # end if
            self.mdadm.Update()
            device = None
            for dev in self.mdadm.Devices:
                if dev.name == self.NewRaid.device_name:
                    device = dev
                    break
                # end if
            # next
            if not device is None:
                # Now create the tab for it
                tabs = self.find('insert_tabs')

                tabTemplate = self.ui.inflate('mdadm:mdadm-tab')
                devTab = tabTemplate.find("device_tab")
                devTab.title = device.name
                devTab.id = device.name

                self.TabBinders.append(( device, devTab, Binder(device, devTab) ))

                devTab.find('addDrive').on('click', self.on_addDevice, device)
                devTab.find('startDevice').on('click', self.on_startDevice, device)
                devTab.find('stopDevice').on('click', self.on_stopDevice, device)
                drive_devices = devTab.find('drive_devices')

                def post_drive_device(obj, coll, item, ui):
                    ui.find('fail-device').on('click', self.on_failDevice, obj, item)
                    ui.find('remove-device').on('click', self.on_removeDevice, obj, item)
                    return

                # end def

                drive_devices.post_item_bind = post_drive_device

                tabs.append(tabTemplate)
                tabs.active = self.TabCount
                self.TabCount += 1
                self.refresh()
            else:
                self.context.notify('error', 'unable to find MD device')
            # end if
        else:
            self.context.notify('error', msg)
        # end if
        return

    # end def

    def on_update_new(self, obj, coll, item):
        binder = self.TabBinders[0][2]
        binder.update()
        binder.setup(obj).populate()
        return

    # end def

    def on_remove_new(self, obj, coll, item):
        coll.remove(item)
        self.TabBinders[0][2].setup(obj).populate()
        return

    # end def

    def on_stopDevice(self, device):
        tabs = self.find('insert_tabs')
        devTab = tabs.find(device.name)
        tabs.remove(devTab)
        self.TabCount -= 1
        self.mdadm.stopDevice(device.name)
        self.mdadm.Update()
        newRaidTab = self.find('new_raid_device')
        adn = newRaidTab.find('active_device_names')
        adn.values = adn.labels = self.getPartions()
        tabs.active = 0
        self.refresh()
        return

    # end def

    def on_startDevice(self, device):
        self.mdadm.startDevice(device.name)
        return

    # end def

    def on_addDevice(self, device):
        self.addToRaid = device
        self.find('add-drive-device').visible = True
        return

    # end def

    @on('add-drive-device', 'submit')
    def on_add_drive_device(self, value):
        err, out = self.mdadm.AddStorageDevice(self.addToRaid.name, value)
        if not err is None and err <> "":
            self.context.notify('error', err)
        # end if
        if not out is None and out <> "":
            self.context.notify('info', out)
        # end if
        self.refresh()
        return

    # end def

    def on_failDevice(self, device, drive):
        err, out = self.mdadm.FailStorageDevice(device.name, drive.name)
        if not err is None and err <> "":
            self.context.notify('error', err)
        # end if
        if not out is None and out <> "":
            self.context.notify('info', out)
        # end if
        self.refresh()
        return

    # end def

    def on_removeDevice(self, device, drive):
        err, out = self.mdadm.RemoveStorageDevice(device.name, drive.name)
        if not err is None and err <> "":
            self.context.notify('error', err)
        # end if
        if not out is None and out <> "":
            self.context.notify('info', out)
        # end if
        self.refresh()
        return

    # end def

    def onUpdate(self):
        self.refresh()
        return

    # end def

    def refresh(self):
        for container, tab, binder in self.TabBinders:
            if not tab is None:
                container.Update()
            # end if
            if not container is None:
                binder.setup(container).populate()
            # end if
        # next
        return

    # end def

# end class
