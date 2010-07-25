from ajenti.utils import *
import re

class Task():
    def __new__(self):
        self.minute = ''
        self.hour = ''
        self.day = ''
        self.month = ''
        self.dow = ''
        
def read_crontab(user="root"):
    tasks = []
    try:
        f = open("/var/spool/cron/crontab/root", "r")
    except:
        return None
    f.readline()
    for line in f.readlines():
        pass
