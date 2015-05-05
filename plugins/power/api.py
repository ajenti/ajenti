import os
import subprocess

from jadi import service


@service
class PowerManager(object):
    def __init__(self, context):
        self.context = context

    def __parse_acpi_value(self, v):
        value, unit = v.split()
        value = float(value)
        if unit.startswith('m'):
            value /= 1000
        return value

    def get_batteries(self):
        batteries = []
        battery_dir = '/proc/acpi/battery'
        if not os.path.exists(battery_dir):
            return []
        for d in sorted(os.listdir(battery_dir)):
            props = {}
            for path in [
                os.path.join(battery_dir, d, 'info'),
                os.path.join(battery_dir, d, 'state'),
            ]:
                for l in open(path).read().splitlines():
                    if ':' in l:
                        key, value = l.strip().split(':')
                        props[key] = value.strip()
            battery = {
                'name': d,
                'designCapacity': self.__parse_acpi_value(props.get('design capacity', '0 Wh')),
                'fullCapacity': self.__parse_acpi_value(props.get('last full capacity', '0 Wh')),
                'capacityLeft': self.__parse_acpi_value(props.get('remaining capacity', '0 Wh')),
                'rate': self.__parse_acpi_value(props.get('present rate', '0 W')),
                'voltage': self.__parse_acpi_value(props.get('present rate', '0 V')),
                'type': props.get('battery type', 'Unknown'),
                'manufacturer': props.get('OEM info', 'Unknown'),
                'charging': props.get('charging state', None) == 'charging',
            }
            batteries.append(battery)
        return batteries

    def get_adapters(self):
        adapters = []
        adapter_dir = '/proc/acpi/ac_adapter'
        if not os.path.exists(adapter_dir):
            return []
        for d in sorted(os.listdir(adapter_dir)):
            props = {}
            path = os.path.join(adapter_dir, d, 'state')
            for l in open(path).read().splitlines():
                if ':' in l:
                    key, value = l.strip().split(':')
                    props[key] = value.strip()
            adapter = {
                'name': d,
                'pluggedIn': props.get('state', None) == 'on-line',
            }
            adapters.append(adapter)
        return adapters

    def poweroff(self):
        subprocess.check_call(['poweroff'])

    def reboot(self):
        subprocess.check_call(['reboot'])

    def suspend(self):
        subprocess.check_call(['pm-suspend'])

    def hibernate(self):
        subprocess.check_call(['pm-hibernate'])
