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
import copy
import time
import subprocess
import logging

import ajenti


log = logging.getLogger()


class RAID_Device(object):
    def __init__(self, mdadm):
        self.drive_type = 'Active'
        self.drive_name = ''
        self.mdadm = mdadm
        return

    # end def

# end class

class NewRaidDevice(object):
    def __init__(self, mdadm):
        self.mdadm = mdadm
        self.enable_mon = True
        self.email = 'root'
        self.device_name = 'md0'
        self.meta_data = '1.2'
        self.new_devices = []
        self.device_type = 1
        names = []
        for device in self.mdadm.Devices:
            names.append(device.name)
        # next
        if len(names) > 0:
            names.sort()
            name = names[len(names) - 1]
            # the should be /dev/md<number>
            self.device_name = "%s%i" % ( name[0:7], int(name[7:]) + 1 )
        # end if
        return

    # end def

# end class

class BlockDevice(object):
    def __init__(self, items=None):
        self.name = ''
        self.id = 0
        self.number = 0
        self.major = 0
        self.minor = 0
        self.state = ''
        self.substate = ''
        self.magic = ''
        self.featureMap = 0
        self.dataOffset = ''
        self.superOffset = ''
        self.checksum = ''
        self.layout = ''
        self.chunkSize = ''
        self.role = ''
        self.UUID = ''
        self.valid = False
        if type(items) == list:
            self.Set(items)
        # end if
        return

    # end def

    def Set(self, items):
        self.number = int(items[0])
        self.major = int(items[1])
        self.minor = int(items[2])
        if items[3] <> '-':
            self.id = int(items[3])
        else:
            self.id = -1
        self.state = items[4]
        offset = 5
        if offset < len(items) and items[offset][0] != '/':
            # print( items[ offset ] )
            self.substate = items[offset]
            offset += 1
        # end if
        if offset < len(items) and items[offset][0] == '/':
            # print( items[ offset ] )
            self.name = items[offset]
            offset += 1
        # end if
        self.Update()
        return

    # end def

    def Update(self):
        process = subprocess.Popen(["mdadm", "--query", "--examine", "%s" % ( self.name )],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        lines = out.splitlines(False)
        for line in lines:
            if line <> "":
                cmd, value = line.split(':', 1)
                cmd = cmd.strip(' ')
                value = value.strip(' ')
                if cmd == 'Magic':
                    self.magic = value
                elif cmd == 'Feature Map':
                    self.featureMap = int(value, 16)
                elif cmd == 'Data Offset':  # 262144 sectors
                    self.dataOffset = value
                elif cmd == 'Super Offset':  # 8 sectors
                    self.superOffset = value
                elif cmd == 'Checksum':
                    self.checksum = value
                elif cmd == 'Layout':
                    self.layout = value
                elif cmd == 'Chunk Size':
                    self.chunkSize = value
                elif cmd == 'Device Role':
                    self.role = value
                elif cmd == 'Device UUID':
                    self.UUID = value
                    # end if
                    # end if
        # next
        self.valid = True
        return

    # end def

    @property
    def State(self):
        if self.state == 'active' and self.substate == 'sync':
            return "Up"
        elif self.state == '_' and self.substate == 'F':
            return "Failed"
        elif self.substate == '':
            return "Down %s" % ( self.state )
        elif self.substate == 'rebuilding':
            return "Up %s - %s" % ( self.state, self.substate )
        # end if
        return "Down %s - %s" % ( self.state, self.substate )
    # end def

# end class

class DeviceStatus(object):
    def __init__(self, name):
        self.name = name
        self.device_binder = None
        self.devices = []
        self.version = 0.0
        self.creationTime = ''
        self.updateTime = ''
        self.type = ''
        self.arraySize = 0
        self.usedDevSize = 0
        self.raidDevices = 0
        self.totalDevices = 0
        self.activeDevices = 0
        self.workingDevices = 0
        self.failedDevices = 0
        self.spareDevices = 0
        self.persistence = ''
        self.status = ''
        self.hostName = ''
        self.UUID = ''
        self.events = 0
        self.progress = 0.0
        self.valid = False
        self.__LastUpdate = 0
        return

    # end def

    def Update(self):
        currentTime = time.time()
        if self.__LastUpdate == 0:
            pass
        elif self.__LastUpdate > currentTime - 10:
            return
        # end if
        self.__LastUpdate = currentTime
        process = subprocess.Popen(["mdadm", "-D", "%s" % ( self.name )],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        out = out.splitlines()
        for device in self.devices:
            device.valid = False
        # end if
        for line in out[1:]:
            cols = line.split(':')
            if len(cols) > 1:
                cols[1] = ":".join(cols[1:])
            # end if
            cols[0] = cols[0].strip(' ')
            if len(cols) > 1:
                cols[1] = cols[1].strip(' ')
                if cols[0] == 'Version':
                    self.version = float(cols[1])
                elif cols[0] == 'Creation Time':
                    self.creationTime = cols[1]
                elif cols[0] == 'Raid Level':
                    self.type = cols[1]
                elif cols[0] == 'Array Size':
                    self.arraySize = int(cols[1].split(' ')[0])
                elif cols[0] == 'Used Dev Size':
                    self.usedDevSize = int(cols[1].split(' ')[0])
                elif cols[0] == 'Raid Devices':
                    self.raidDevices = int(cols[1])
                elif cols[0] == 'Total Devices':
                    self.totalDevices = int(cols[1])
                elif cols[0] == 'Persistence':
                    self.persistence = cols[1]
                elif cols[0] == 'Update Time':
                    self.updateTime = cols[1]
                elif cols[0] == 'State':
                    self.status = cols[1].split(',')
                    for i in range(0, len(self.status)):
                        self.status[i] = self.status[i].strip(' ')
                    # next
                elif cols[0] == 'Active Devices':
                    self.activeDevices = int(cols[1])
                elif cols[0] == 'Working Devices':
                    self.workingDevices = int(cols[1])
                elif cols[0] == 'Failed Devices':
                    self.failedDevices = int(cols[1])
                elif cols[0] == 'Spare Devices':
                    self.spareDevices = int(cols[1])
                elif cols[0] == 'Name':
                    self.hostName = cols[1]
                elif cols[0] == 'UUID':
                    self.UUID = cols[1]
                elif cols[0] == 'Events':
                    self.events = int(cols[1])
                elif cols[0] == 'Rebuild Status':
                    self.progress = float(cols[1].replace('% complete', ''))
                # end if
            elif len(cols) > 0:
                if len(cols[0]) > 0 and cols[0][0].isdigit():
                    dev = None
                    cols[0] = cols[0].replace('        ', ';').replace('       ', ';').replace('      ', ';').replace(
                        '   ', ';').replace(' ', ';')
                    items = cols[0].split(';')
                    if items[len(items) - 1] != 'removed':
                        # print( items )
                        for device in self.devices:
                            if device.name == items[len(items) - 1]:
                                dev = device
                                dev.Set(items)
                                dev.Update()
                                # end if
                        # next
                        if dev is None:
                            dev = BlockDevice(items)
                            dev.Update()
                            self.devices.append(dev)
                        # end if
                    # end if
                # end if
            # end if
        # next
        for device in self.devices:
            if not device.valid:
                self.devices.remove(device)
            # end if
        # next
        return

    # end def

    @property
    def typeUpdate(self):
        if "recovering" in self.status or "resync" in self.status:
            return "Recovery:"
        elif self.checking:
            return "Checking:"
        # end if
        return ""

    # end def

    @property
    def resync(self):
        return "resync" in self.status

    # end def

    @property
    def checking(self):
        return "checking" in self.status

    # end def

    @property
    def degraded(self):
        return "degraded" in self.status

    # end def

    @property
    def showRecovery(self):
        return "recovering" in self.status or "checking" in self.status or "resync" in self.status

    # end def

    @property
    def stateText(self):
        status = ",".join(self.status)
        if self.resync or self.checking:
            if self.resync:
                return "%s, syncing: %.2f%%" % ( status, self.progress )
            else:
                return "%s, checking: %.2f%%" % ( status, self.progress )
            # end if
        # end if
        return status

    # end def

    @property
    def ProgressBar(self):
        return self.progress / 100

    # end if

    @property
    def degraded(self):
        for idx in range(0, len(self.devices)):
            dev = self.devices[idx]
            if not dev is None:
                if dev.state in ["removed", "faulty"]:
                    return True
                # end if
            # end if
        # next
        return False
    # end def

# end class

class MdadmStatus(object):
    ubuntu_conf_location = '/etc/mdadm/mdadm.conf'
    default_conf_location = '/etc/mdadm.conf'

    def __init__(self):
        self.version = None
        self.Personalities = []
        self.UnusedDevices = []
        self.Devices = []
        self.__LastUpdate = 0
        self.IO_Controller = ''
        self.configFile = self.default_conf_location
        if ajenti.platform_unmapped == 'ubuntu':
            self.configFile = self.ubuntu_conf_location
        # end if
        return

    # end def

    def SetValue(self, line):
        name, value = line.split(':', 1)
        name = name.strip(' ').replace('/', '').replace(' ', '_')
        value = value.strip(' ')
        setattr(self, name, value)
        return

    # end def

    def Update(self):
        currentTime = time.time()
        if self.__LastUpdate == 0:
            pass
        elif self.__LastUpdate > currentTime - 10:
            return
        # end if
        self.__LastUpdate = currentTime
        process = subprocess.Popen(["mdadm", "--detail-platform"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        out = err + out
        lines = out.splitlines(False)
        del lines[0]
        for line in lines:
            self.SetValue(line)
        # next
        log.debug("I/O Controller: %s" % ( self.IO_Controller ))

        mdstat = open('/proc/mdstat').read().splitlines(False)
        self.Personalities = []
        self.UnusedDevices = []
        self.Devices = []
        DeviceList = []

        for line in mdstat:
            cols = line.split(':')
            if len(cols) == 1:
                # belongs to current device
                data = cols[0].replace('  ', ' ').strip(' ').split(' ')
            else:
                if cols[0] == 'Personalities ':
                    data = cols[1].strip(' ').replace('[', '').replace(']', '')
                    self.Personalities = data.split(' ')
                elif cols[0] == 'unused devices':
                    data = cols[1].strip(' ')
                    if data <> '<none>':
                        self.UnusedDevices = data.split(' ')
                        # end if
                else:
                    data = cols[1].split(' ')
                    obj = {'name': '/dev/%s' % ( cols[0].strip(' ') ),
                           'status': data[1],
                           'type': data[2]}
                    DeviceList.append(obj)
                # end if
            # end if
        # next
        oldList = copy.copy(self.Devices)
        self.Devices = []
        for devDict in DeviceList:
            found = False
            for device in oldList:
                if device.name == devDict['name']:
                    found = True
                    device.status = devDict['status']
                    device.Update()
                    self.Devices.append(device)
                # end if
            # next
            if not found:
                device = DeviceStatus(devDict['name'])
                device.status = devDict['status']
                device.type = devDict['type']
                device.Update()
                self.Devices.append(device)
            # end if
        # next
        self.Devices.sort(key=lambda x: x.name, reverse=False)
        return

    # end def

    def __execute(self, args):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err, out = process.communicate()
        if 'error' in out:
            tmp = err
            err = out
            out = tmp
        # end if
        return ( out, err )

    # end def

    def RemoveStorageDevice(self, raid_device, drive_device):
        # mdadm /dev/<name> --remove /dev/<name>
        return self.__execute(["mdadm", raid_device, "--remove", drive_device])

    # end def

    def FailStorageDevice(self, raid_device, drive_device):
        # mdadm /dev/<raid_device> --fail /dev/<drive_device>
        return self.__execute(["mdadm", raid_device, "--fail", drive_device])

    # end def

    def AddStorageDevice(self, raid_device, drive_device):
        # mdadm /dev/<name> --add /dev/<name>
        return self.__execute(["mdadm", raid_device, "--add", drive_device])

    # end def

    def stopDevice(self, raid_device):
        # mdadm --stop /dev/<name>
        return self.__execute(["mdadm", "--stop", raid_device])

    # end def

    def startDevice(self, raid_device):
        # mdadm -A --config /etc/mdadm.conf /dev/<name>
        return self.__execute(["mdadm", "--assemble", "--config", "/etc/mdadm.conf", raid_device])

    # end def

    def createDevice(self, dNname, dType, dMeta, activeDevices, spareDevices, monitor):
        cmd = ['mdadm', '--create', '--verbose', '--run', dNname,
               '--metadata', dMeta,
               '--level', str(dType),
               '--raid-devices', str(len(activeDevices))]
        for dev in activeDevices:
            cmd.append(dev)
        # next
        if len(spareDevices) > 0:
            cmd.extend(['--spare-devices', str(len(spareDevices))])
            for dev in spareDevices:
                cmd.append(dev)
            # next
        # end if
        startedMsg = "mdadm: array %s started." % ( dNname )
        out, err = self.__execute(cmd)
        if startedMsg in out:
            if monitor[0]:
                out, err = self.__execute(
                    ['mdadm', '--monitor', '--daemonize', '--mail=%s' % ( monitor[1] ), '--delay=1800', dNname])
                if not "error" in out and err == "":
                    out, err = self.__execute(['mdadm', '--monitor', '--scan', '--test', '--oneshot'])
                # end if
            # end if
            return ( True, out + err )
        else:
            log.debug("Status: 'not ok' %s:%s" % ( out, err ))
        # end if
        return ( False, out + err )

    # end def

    def getVersion(self):
        if self.version is None:
            out, err = self.__execute(['mdadm', '--version'])
            self.version = out.replace('mdadm - ', '').strip()
        # end if
        return self.version

    # end def

# end class



mdadm = MdadmStatus()


def getMdadmStatus():
    global mdadm
    return mdadm

# end if

if __name__ == '__main__':
    test_mdadm = getMdadmStatus()
    while ( True ):
        test_mdadm.Update()
        test_mdadm.Dump()
        time.sleep(5)
    # end while
# end if
