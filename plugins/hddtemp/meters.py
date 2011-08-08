#coding: utf-8

from ajenti.api import *
from ajenti.utils import shell
import os
import re


class HDDTempMeter (DecimalMeter):
    name = 'HDD temperature'
    category = 'System'
    transform = 'float'

    def list_disks(self):
        r = []
        for s in os.listdir('/dev'):
            if re.match('sd.$|hd.$|scd.$|fd.$|ad.+$', s):
                r.append(s)
        return sorted(r)

    def get_variants(self):
        return self.list_disks()

    def init(self):
        self.text = self.variant + ', °C'

    def get_value(self):
        return float('0'+shell('hddtemp /dev/%s -uC -qn 2> /dev/null'%self.variant).strip())
