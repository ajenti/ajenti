# verify subprocess.check_output
import subprocess

if not hasattr(subprocess, 'check_output'):
    def c_o(*args, **kwargs):
        popen = subprocess.Popen(stdout=subprocess.PIPE, stderr=subprocess.PIPE, *args, **kwargs)
        popen.wait()
        return popen.stdout.read() + popen.stderr.read()
    subprocess.check_output = c_o
