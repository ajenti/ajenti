import re

def hx(m):
    return chr(int(m.group(1), 16))

def URLDecode(s):
    return re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M).sub(hx, s)
