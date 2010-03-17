import re
import tools
import platform


def hx(m):
    return chr(int(m.group(1), 16))

def url_decode(s):
    return re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M).sub(hx, s)

_platform = 'unknown'
  
def detect_platform():
	global _platform
	
	if _platform != 'unknown':
		return _platform
		
	if platform.system() != 'Linux':
		_platform = platform.system().lower()
		return _platform

	(maj, min, patch) = platform.python_version_tuple()
	if (maj * 10 + min) >= 26:
		_platform = platform.linux_distribution()[0]
	else:
		_platform = platform.dist()[0]

	if _platform == '':
		_platform = 'generic'
	
	return _platform
