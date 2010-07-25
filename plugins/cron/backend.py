from ajenti.utils import *
import re

class Task():
    def __new__(self):
        self.minute = ''
        self.hour = ''
        self.day = ''
        self.month = ''
        self.dow = ''
        
