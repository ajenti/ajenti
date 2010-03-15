import re
import tools

def hx(m):
    return chr(int(m.group(1), 16))

def URLDecode(s):
    return re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M).sub(hx, s)

platform = 'generic'
  
def detect_platform():
	global platform
	if platform != 'generic':
		return platform
		
	if tools.Actions['core/shell-status'].Run('cat /etc/issue | grep Fedora') == 0:
		platform = 'fedora'
	if tools.Actions['core/shell-status'].Run('cat /etc/issue | grep Ubuntu') == 0:
		platform = 'ubuntu'
	if tools.Actions['core/shell-status'].Run('test -e /etc/debian_version') == 0:
		platform = 'debian'

	return platform
